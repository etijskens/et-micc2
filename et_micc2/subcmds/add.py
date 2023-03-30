import os
from pathlib import Path

import et_micc2.tools.env as env
import et_micc2.tools.expand as expand
import et_micc2.tools.messages as messages
from et_micc2.tools.tomlfile import TomlFile
import et_micc2.tools.utils as utils


def add(project):
    """Add a component to the project."""

    key = project.components.has_name(project.context.add_name)
    if key:
        messages.error(
            f"It is recommended that component names are unique. Component '{key}' exists already.",
            exit_code=messages.ExitCodes.COMPONENT_NAME_NOT_UNIQUE.value
        )

    # set implied flags:
    if project.context.flag_clisub:  # cli with subcommands
        app_implied = f" [implied by --clisub   ({int(project.context.flag_clisub)})]"
        project.context.flag_cli = True
    else:
        app_implied = ""

    if project.context.flag_cli:
        # Prepare for adding a cli component
        cli = Cli(project.context)
        db_entry = cli.create()

    else:
        # Prepare for adding a submodule
        submodule = Submodule(project)
        db_entry = submodule.create()

    project.serialize(db_entry)

class Submodule:
    def __init__(self, project):
        """
        :param context: project context
        """
        self.logger = project.logger
        self.context = project.context
        p_add_name = Path(self.context.add_name)
        self.context.module_location_relative = p_add_name.parent
        self.context.module_name = p_add_name.name
        self.context.module_srcdir = Path(self.context.package_name) / p_add_name
        self.context.import_lib = str(self.context.module_srcdir).replace(os.sep,".")
        self.context.template_parameters.update(
            { 'module_name': self.context.module_name
            , 'source_dir' : self.context.module_srcdir
            , 'import_lib' : self.context.import_lib
            }
        )

        # Verify that the module_name is not already used:
        if (self.context.project_path / self.context.package_name / self.context.module_location_relative / self.context.module_name).is_dir():
            messages.error(f"Project {self.context.project_path.name} has already a module named {self.context.import_lib}.")

        # Verify that the name is valid:
        pep8_module_name = utils.pep8_module_name(self.context.module_name)
        if (not utils.verify_project_name(self.context.module_name)
            or self.context.module_name != pep8_module_name
           ):
            suggest = f'Suggesting: "{pep8_module_name}".' if utils.verify_project_name(pep8_module_name) else ''
            messages.error(
                f"Not a valid module name ({self.context.module_name}). Valid names:\n"
                f"  * start with a letter [a-z]\n"
                f"  * contain only lowercase letters [a-z], digits, and underscores\n"
                f"{suggest}"
            )

        # Verify theat the parent is a python package
        parent = self.context.project_path / self.context.package_name / self.context.module_location_relative
        if not (parent / '__init__.py').is_file():
            messages.error(
                f"The parent of a submodule must be a python package.\n"
                f"    {parent} is not a Python package."
            )


    def create(self):
        """Create a submodule."""

        db_entry = {'context': self.context}

        if self.context.flag_py:
            # prepare for adding a Python submodule:
            self.context.templates = ['submodule-py', 'submodule-py-test']
            self.add_python_submodule(db_entry)

        else: # add a binary extension module

            if self.context.flag_f90:
                # Warn if f2py is not available
                env.check_f2py()
                # prepare for adding a Fortran submodule:
                self.context.templates = ['submodule-f90', 'submodule-f90-test']
                self.add_f90_submodule(db_entry)

            if self.context.flag_cpp:
                # Warn if cmake is not available
                env.check_cmake()
                # Warn if pybind11 is not available or too old
                env.check_pybind11()

                # prepare for adding a C++ submodule:
                self.context.templates = ['submodule-cpp', 'submodule-cpp-test']
                self.add_cpp_submodule(db_entry)

        return db_entry


    def add_python_submodule(self, db_entry):
        """

        :param db_entry:
        """
        with messages.log(
                self.logger.info,
                f"Adding python submodule {self.context.add_name} to package {self.context.package_name}."
            ):

            # Create the needed folders and files by expanding the templates:
            msg = expand.expand_templates(self.context)
            if msg:
                self.logger.critical(msg)
                return

            src_file = self.context.project_path / self.context.package_name / self.context.add_name / '__init__.py'
            tst_file = self.context.project_path / 'tests' / self.context.package_name / self.context.add_name / f'test_{self.context.module_name}.py'

            self.logger.info(f"- python source in    {src_file}.")
            self.logger.info(f"- Python test code in {tst_file}.")

            with utils.in_directory(self.context.project_path):
                # docs
                filename = "API.rst"
                text = f"\n.. automodule:: {self.context.package_name}.{self.context.add_name.replace(os.sep,'.')}" \
                        "\n   :members:\n\n"
                with open(filename, "a") as f:
                    f.write(text)
                db_entry[filename] = text

            self.add_import_code(db_entry)


    def add_f90_submodule(self, db_entry):
        """Add a f90 module to this project."""
        with messages.log(
                self.logger.info,
                f"Adding f90 submodule {self.context.add_name} to package {self.context.package_name}."
            ):

            # Create the needed folders and files by expanding the templates:
            msg = expand.expand_templates(self.context)
            if msg:
                self.logger.critical(msg)
                return

            src_file = self.context.project_path / self.context.package_name / self.context.add_name / (self.context.module_name+'.f90')
            cmk_file = self.context.project_path / self.context.package_name / self.context.add_name / 'CMakeLists.txt'
            rst_file = self.context.project_path / self.context.package_name / self.context.add_name / (self.context.module_name+'.rst')
            tst_file = self.context.project_path / 'tests' / self.context.package_name / self.context.add_name / f'test_{self.context.module_name}.py'

            self.logger.info(f"- Fortran source in       {src_file}.")
            self.logger.info(f"- build settings in       {cmk_file}.")
            self.logger.info(f"- module documentation in {rst_file} (restructuredText format).")
            self.logger.info(f"- Python test code in     {tst_file}.")

            with utils.in_directory(self.context.project_path):
                # docs
                filename = "API.rst"
                text = f"\n.. include:: ../{self.context.package_name}/{self.context.module_location_relative}/{self.context.module_name}/{self.context.module_name}.rst\n"
                with open(filename, "a") as f:
                    f.write(text)
                db_entry[filename] = text

        self.add_auto_build_code(db_entry)


    def add_auto_build_code(self, db_entry):
        """Add auto build code for binary extension modules in :file:`__init__.py` of the package."""
        module_name = self.context.add_name
        import_lib = self.context.import_lib
        text_to_insert = [
            f"",
            f"from et_micc2.subcmds.build import build_missing",
            f"build_missing(__file__, '{module_name}')",
            f"import {import_lib}",
        ]
        file = os.path.join(self.context.package_name, '__init__.py')
        utils.insert_in_file(
            self.context.project_path / file,
            text_to_insert,
            startswith="__version__ = ",
        )
        text = '\n'.join(text_to_insert)
        db_entry[file] = text

    def add_cpp_submodule(self, db_entry):
        """Add a cpp module to this project."""
        with messages.log(
                self.logger.info,
                f"Adding cpp submodule {self.context.add_name} to package {self.context.package_name}."
            ):
            msg = expand.expand_templates(self.context)
            if msg:
                self.logger.critical(msg)
                return

            src_file = self.context.project_path /           self.context.package_name / self.context.add_name / (self.context.module_name+'.cpp')
            cmk_file = self.context.project_path /           self.context.package_name / self.context.add_name / 'CMakeLists.txt'
            rst_file = self.context.project_path /           self.context.package_name / self.context.add_name / (self.context.module_name+'.rst')
            tst_file = self.context.project_path / 'tests' / self.context.package_name / self.context.add_name / f'test_{self.context.module_name}.py'
            self.logger.info(f"- C++ source in           {src_file}.")
            self.logger.info(f"- build settings in       {cmk_file}.")
            self.logger.info(f"- module documentation in {rst_file} (restructuredText format).")
            self.logger.info(f"- Python test code in     {tst_file}.")

            with utils.in_directory(self.context.project_path):
                # docs
                with open("API.rst", "a") as f:
                    filename = "API.rst"
                    text = f"\n.. include:: ../{self.context.package_name}/{self.context.module_location_relative}/{self.context.module_name}/{self.context.module_name}.rst\n"
                    with open(filename, "a") as f:
                        f.write(text)
                    db_entry[filename] = text

        self.add_auto_build_code(db_entry)


    def add_import_code(self, db_entry):
        """Add import statement for this python s in :file:`__init__.py` of the package."""
        module_name = self.context.add_name
        text_to_insert = [ ""
                         , f"import {self.context.package_name}.{self.context.add_name.replace(os.sep,'.')}"
                         ]
        file = os.path.join(self.context.package_name, '__init__.py')
        utils.insert_in_file(
            self.context.project_path / file,
            text_to_insert,
            startswith="__version__ = ",
        )
        text = '\n'.join(text_to_insert)
        db_entry[file] = text


def get_submodule_type(path):
    """Find out the type of submodule.

    :param path: path to submodule directory
    :return: "py", "cpp", "f90", or None
    """
    if (path / '__init__.py').is_file():
        return 'py'
    if (path / (path.name + '.f90')).is_file():
        return 'f90'
    if (path / (path.name + '.cpp')).is_file():
        return 'cpp'


class Cli:
    def __init__(self, context):
        self.context = context
        app_name = self.context.add_name
        if os.sep in app_name:
            messages.error(
                f"CLIs are automatically placed in the '{context.package_name}/cli' directory. "
                f"The name ('{app_name}') must not be path-like."
            )

        if (context.project_path / context.package_name / 'cli' / f"{app_name}.py").is_file():
            messages.error(f"Project {self.context.project_path.name} has already an app named {app_name}.")

        if not utils.verify_project_name(app_name):
            messages.error(
                f"Not a valid app name ({app_name}_. Valid names:\n"
                f"  * start with a letter [a-zA-Z],\n"
                f"  * contain only [a-zA-Z], digits, underscores, and hyphens.\n"
            )

    def create(self):
        """Add a console script (app, aka CLI) to the package."""
        db_entry = {'context': self.context}

        if self.context.flag_clisub:
            self.context.templates = ['app-sub-commands']
            cli_type = '(CLI with subcommands)'
        else:
            self.context.templates = ['app-single-command']
            cli_type = '(single command CLI)'

        app_name = self.context.add_name
        cli_app_name = 'cli/' + utils.pep8_module_name(app_name)

        with messages.log(
                self.context.logger.info, 
                f"Adding CLI {app_name} to project {self.context.project_path.name}\n"
                f"    {cli_type}."
            ):
            self.context.template_parameters.update(
                {'app_name': app_name}
            )

            msg = expand.expand_templates(self.context)
            if msg:
                self.context.logger.critical(msg)
                return

            package_name = self.context.template_parameters['package_name']
            src_file = os.path.join(self.context.project_path.name, package_name, 'cli', f"{app_name}.py")
            tst_file = os.path.join(self.context.project_path.name, 'tests', 'cli', f"test_{app_name}.py")
            self.context.logger.info(f"- Python source file {src_file}.")
            self.context.logger.info(f"- Python test code   {tst_file}.")

            with utils.in_directory(self.context.project_path):
                # docs
                # Look if this package has already an 'apps' entry in docs/index.rst
                with open('docs/index.rst', "r") as f:
                    lines = f.readlines()
                has_already_apps = False
                api_line = -1
                for l, line in enumerate(lines):
                    has_already_apps = has_already_apps or line.startswith("   apps")
                    if line.startswith('   api'):
                        api_line = l

                # if not, create it:
                if not has_already_apps:
                    lines.insert(api_line, '   apps\n')
                    with open('docs/index.rst', "w") as f:
                        for line in lines:
                            f.write(line)
                # Create 'APPS.rst' if it does not exist:
                txt = ''
                if not Path('APPS.rst').exists():
                    # create a title
                    title = "Command Line Interfaces (apps)"
                    line = len(title) * '*' + '\n'
                    txt += (line
                            + title + '\n'
                            + line
                            + '\n'
                            )
                # create entry for this apps documentation
                txt2 = (f".. click:: {package_name}.cli.{app_name}:main\n"
                        f"   :prog: {app_name}\n"
                        f"   :show-nested:\n\n"
                        )
                file = 'APPS.rst'
                with open(file, "a") as f:
                    f.write(txt + txt2)
                db_entry[file] = txt2

                # pyproject.toml
                add_dependencies(self.context, {'click': '^7.0.0'})
                pyproject_toml = TomlFile(self.context.project_path / 'pyproject.toml')
                pyproject_toml['tool']['poetry']['scripts'][app_name] = f"{package_name}:{cli_app_name}.main"
                pyproject_toml.save()
                # huh?
                db_entry['pyproject.toml'] = f'{app_name} = "refactoring_dev:cli_{app_name}.main"\n'

                # This does not seem very useful:
                # add 'import <package_name>.cli_<app_name> to __init__.py
                # line = f"import {package_name}.{app_name}\n"
                # file = self.context.project_path / self.context.package_name / '__init__.py'
                # utils.insert_in_file(file, [line], before=True, startswith="__version__")
                # db_entry[os.path.join(self.context.package_name, '__init__.py')] = line

        return db_entry


def add_dependencies(context, deps):
    """Add dependencies to the :file:`pyproject.toml` file.

    :param dict deps: (package,version_constraint) pairs.
    """
    pyproject_toml = TomlFile(context.project_path / 'pyproject.toml')
    tool_poetry_dependencies = pyproject_toml['tool']['poetry']['dependencies']
    modified = False
    for pkg, version_constraint in deps.items():
        if pkg in tool_poetry_dependencies:
            # project was already depending on this package
            range1 = utils.version_range(version_constraint)
            range2 = utils.version_range(tool_poetry_dependencies[pkg])
            if range1 == range2:
                # nothing to do: new and old version specifcation are the same
                continue
            intersection = utils.intersect(range1, range2)
            if utils.validate_intersection(intersection):
                range = intersection
            else:
                range = utils.most_recent(version_constraint, tool_poetry_dependencies[pkg])
            tool_poetry_dependencies[pkg] = utils.version_constraint(range)
            modified = True
        else:
            # an entirely new dependency
            tool_poetry_dependencies[pkg] = version_constraint
            modified = True

    if modified:
        pyproject_toml.save()
        # Tell the user how to add the new dependencies
        msg = 'Dependencies added:\n' \
              'If you are using a virtual environment created with poetry, run:\n' \
              '    `poetry install` or `poetry update` to install missing dependencies.\n' \
              'If you are using a virtual environment not created with poetry, run:\n'
        for dep, version in deps.items():
            msg += f'    (.venv) > pip install {dep}\n'
        msg += 'Otherwise, run:\n'
        for dep, version in deps.items():
            msg += f'    > pip install {dep} --user'
        context.logger.warning(msg)
