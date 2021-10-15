# -*- coding: utf-8 -*-

"""
Module et_micc2.project
=======================

An OO interface to *micc* projects.

"""
from copy import copy
import os, sys, site, subprocess, re
import sysconfig
import shutil
import json
from pathlib import Path
from operator import xor
import requests
from types import SimpleNamespace
from importlib import import_module

import click
import semantic_version

import et_micc2.config
import et_micc2.utils
import et_micc2.expand
import et_micc2.logger
from et_micc2.tomlfile import TomlFile
import pkg_resources


__FILE__ = Path(__file__).resolve()


def micc_version():
    return et_micc2.__version__


def on_vsc_cluster():
    """test if we are running on one of the VSC clusters"""
    try:
        os.environ['VSC_HOME']
        os.environ['VSC_INSTITUTE_CLUSTER']
    except:
        return False
    else:
        return True


def is_os_tool(path_to_exe):
    """test if path_to_exe was installed as part of the OS."""
    return path_to_exe.startswith('/usr/bin')


class PkgInfo:
    mock = [] # list of module names to pretend missing. This is just for testing purposes.

    def __init__(self, pkg_name):
        if pkg_name in PkgInfo.mock:
            print(f'Mock: pretending module `{pkg_name}` is missing.')
            self.which = ''
        else:
            try:
                self.pkg_dist_info = pkg_resources.get_distribution(pkg_name)
            except pkg_resources.DistributionNotFound:
                self.which = ''
            else:
                self.which = self.pkg_dist_info.location

    def is_available(self):
        """Return True if the tool is available, False otherwise."""
        return bool(self.which)

    def version(self):
        """Return the version string of the tool, or an empty string if the tool is not available."""
        return self.pkg_dist_info.version if self.which else ''


__pybind11_required_version__ = '2.6.2'


class ToolInfo:
    mock = [] # list of executable names to pretend missing. This is just fortesting purposes.

    def __init__(self, exe, accept_cluster_os_tools=False):
        """Check if tool 'exe' is available.

        :param str exe: name of an executable
        :param bool accept_cluster_os_tools: accept cluster operating system tools


        :return: SimpleNamespace(which,version), where which is the location of the tool or an empty
            string if it is not found or not accepted, and version is the version string (if requested)
            as returned be 'exe --version'.
        """
        self.exe = exe
        if exe in ToolInfo.mock:
            print(f'Mock: pretending tool `{exe}` is missing.')
            self.which = ''
        else:
            # completed_which = subprocess.run(['which', exe], capture_output=True, text=True)
            # self.which = completed_which.stdout.strip().replace('\n', ' ')
            self.which = shutil.which(exe)

        if self.which:
            if on_vsc_cluster() and not accept_cluster_os_tools and is_os_tool(self.which):
                self.which = ''

    def is_available(self):
        """Return True if the tool is available, False otherwise."""
        return bool(self.which)

    def version(self):
        """Return the version string of the tool, or an empty string if the tool is not available."""
        if self.which:
            completed_version = subprocess.run([self.exe, '--version'], capture_output=True, text=True)
            self.version = completed_version.stdout.strip().replace('\n\n','\n')#.replace('\n','\n        ')
        else:
            self.version = ''
        return self.version

_exit_missing_component = -1


def is_project_directory(path, project=None):
    """Verify that the directory :file:`path` is a project directory. 

    :param Path path: path to a directory.
    :param Project project: if not None these variables are set:

        * project.project_name
        * project.package_name
        * project.pyproject_toml

    :returns: bool.

    As a sufficident condition, we request that 

    * there is a pyproject.toml file, exposing the project's name:py:obj:`['tool']['poetry']['name']`
    * that there is a python package or module with that name, converted by :py:meth:`pep8_module_name`.
    """
    if not isinstance(path, Path):
        path = Path(path)

    path_to_pyproject_toml = str(path / 'pyproject.toml')

    try:
        pyproject_toml = TomlFile(path_to_pyproject_toml)
        if not project is None:
            project.pyproject_toml = pyproject_toml
            # project.project_name = project_name
    except Exception:
        return False

    return verify_project_structure(path, project)


def verify_project_structure(path, project=None):
    """Verify that there is either a Python module :file:`<package_name>.py`, or
    a package :file:`<package_name>/__init__.py` (and not both).

    :returns: a list with what was found. This list should have length 1. If its
        length is 0, neither module.py, nor module/__init__.py were found. If its
        length is 2, both were found.
    """
    package_name = et_micc2.utils.pep8_module_name(path.name)

    module = path / (package_name + ".py")
    module = str(module.relative_to(path)) if module.is_file() else ""

    package = path / package_name / "__init__.py"
    package = str(package.relative_to(path)) if package.is_file() else ""

    if package and module:
        if project:
            error(f"Package ({package_name}/__init__.py) and module ({package_name}.py) found.")
        return False
    elif (not module and not package):
        if project:
            error(f"Neither package ({package_name}/__init__.py) nor module ({package_name}.py) found.")
        return False
    else:
        if project:
            project.context.package_name = package_name
        return True


def error(msg, exit_code=1, raise_runtimeerror=True):
        """Print an error message,  set this project's exit_code, and optionally raise a
        RuntimeError.

        :param str msg: the error message
        :param int exit_code: the exit_code to set
        :param bool raise_runtimeerror: raise RuntimeError if True
        """
        click.secho("[ERROR]\n" + msg, fg='bright_red')
        if raise_runtimeerror:
            raise RuntimeError(msg,exit_code)


def warning(msg):
    """Print an warning message ``msg``."""
    click.secho("[WARNING]\n" + msg, fg='green')

def ask_user_to_continue_or_not(default=False, stop_message='Exiting.'):
        """Ask the user if he wants to continue or stop a command.

        If the answer is to stop, sets self.exit_code to -1, and prints the stop_message.

        :param bool default: The answer if the user just presses enter.
        :return: True if the user wants to stop, False otherwise.
        """
        if default == True:
            question = 'Continue? [Yes]/No'
        else:
            question = 'Continue? [No]/Yes'
        answer = input(question)

        if not answer:
            answer = default
        else:
            answer = answer.lower()
            answer = True if answer.startswith('y') else False

        if not answer:
            error(stop_message, exit_code=_exit_missing_component)
            
            
class Project:
    """
    An OO interface to *micc* projects.

    :param types.SimpleNameSpace context: all options from the ``micc`` CLI.
    """

    def __init__(self, context):
        self.context = context

        if hasattr(context, 'template_parameters'):
            # only needed for expanding templates.
            # Pick up the default parameters
            parameters = self.context.preferences
            parameters.update(context.template_parameters)
            context.template_parameters = parameters

        self.logger = None
        if is_project_directory(self.context.project_path, self):
            self.get_logger()
        else:
            # Not a project directory, only create and setup subcommands can work,
            # (but setup does not construct a Project object).
            if not self.context.invoked_subcommand in ('create',):
                error(f'Not a project directory: `{self.context.project_path}`')
 

    def create_cmd(self):
        """Create a new project skeleton."""

        # Check for tools needed:
        # . git is required for creating a local repo
        # . gh is required for creating a remote repo
        
        if self.context.project_path.exists() and os.listdir(str(self.context.project_path)):
            error(
                f"Cannot create project in ({self.context.project_path}):\n"
                f"  Directory must be empty."
            )
        
        toolinfo_git = ToolInfo('git')
        if not self.context.no_git and not toolinfo_git.is_available():
            if on_vsc_cluster():
                warning(
                    'Your current environment has no suitable git command.\n'
                    'Load a cluster module that has git.\n'
                    'If you continue, this project will NOT have a local git repository.'
                )
            else:
                warning(
                    'Your current environment has no git command.\n'
                    'To install git: https://git-scm.com/downloads.\n'
                    'If you continue, this project will NOT have a local git repository.'
                )

            self.ask_user_to_continue_or_not(stop_message='Project not created.')

        if self.context.remote != 'none':
            # Check that we have github username
            github_username = self.context.template_parameters['github_username']
            if not github_username:
                error(
                    'Micc2 configuration does not have a github username. Creation of remote repo is not possible.\n'
                    'Project is not created.'
                )
            # Check availability of gh command:
            if not ToolInfo('gh').is_available() and self.context.remote:
                warning(
                    'The gh command is not available in your environment.\n'
                    'If you continue this project a remote repository will not be created.'
                )
                self.ask_user_to_continue_or_not(stop_message='Project not created.')

        if not self.context.allow_nesting:
            # Prevent the creation of a project inside another project
            p = self.context.project_path.parent.resolve()
            while not p.samefile(os.sep):
                if is_project_directory(p):
                    error(
                        f"Cannot create project in ({self.context.project_path}):\n"
                        f"  Specify '--allow-nesting' to create a et_micc2 project inside another et_micc2 project ({p})."
                    )
                p = p.parent

        # Proceed creating the project
        self.context.project_path.mkdir(parents=True, exist_ok=True)

        if not self.context.module_name:
            # derive package name from project name
            if not et_micc2.utils.verify_project_name(self.context.project_path.name):
                error(
                    f"The project name ({project_name}) does not yield a PEP8 compliant module name:\n"
                    f"  The project name must start with char, and contain only chars, digits, hyphens and underscores.\n"
                    f"  Alternatively, provide an explicit module name with the --module-name=<name>."
                )
            else:
                self.context.package_name = et_micc2.utils.pep8_module_name(self.context.project_path.name)
        else:
            self.context.package_name = self.context.module_name

        try:
            relative_project_path = self.context.project_path.relative_to(Path.cwd())
        except ValueError:
            # project_path was specified relative to cwd using ../
            # use full path instead of relative path
            relative_project_path = self.context.project_path

        if self.context.publish:
            rv = et_micc2.utils.existsOnPyPI(self.context.package_name)
            if rv is False:
                pass # the name is not yet in use
            else:
                if rv is True:
                    error(
                        f"    The name '{self.context.package_name}' is already in use on PyPI.\n"
                        f"    The project is not created.\n"
                        f"    You must choose another name if you want to publish your code on PyPI."
                    )
                elif isinstance(rv, requests.exceptions.ConnectionError):
                    error(f"    ConnectionError: Check your internect connection.\n"
                          f"    The availability of name '{self.context.package_name}' on PyPI could not be verified. \n"
                          f"    The project is not created."
                    )
                else: # unknown error
                    error(
                        f"    {type(rv)}\n"
                        f"    {str(rv)}\n"
                        f"    The availability of name '{self.context.package_name}' on PyPI could not be verified. \n"
                        f"    The project is not created."
                    )

        source_file = str(relative_project_path / self.context.package_name / '__init__.py')

        self.context.verbosity = max(1, self.context.verbosity)

        # The project directory is created, so we can get ourselves a logger:
        self.get_logger()

        with et_micc2.logger.logtime(self):
            with et_micc2.logger.log( self.logger.info
                                    , f"Creating project directory ({self.context.project_path.name}):"
                                    ):
                self.logger.info(f"Python top-level package ({self.context.package_name}):")

                # project_name must come before github_repo because the value of github_repo depends on project_name
                template_parameters = et_micc2.config.Config( project_name=self.context.project_path.name
                                                            , package_name=self.context.package_name )
                template_parameters.update(self.context.template_parameters.data)
                self.context.template_parameters = template_parameters

                self.context.overwrite = False
                msg = et_micc2.expand.expand_templates(self.context)
                if msg:
                    self.logger.critical(msg)
                    self.logger.info(f'Cleaning up after failure...')
                    # Remove the project directory
                    self.context.project_path.unlink()
                    return

                proj_cfg = self.context.project_path / 'micc3.cfg'
                self.context.template_parameters.save(proj_cfg)

                # add git support if requested
                if self.context.no_git:
                    self.logger.warning(
                        f"Flag `--no-git` specified: project `{self.context.project_path.name}` created without git support."
                    )
                else:
                    with et_micc2.logger.log(self.logger.info, "Creating local git repository"):
                        with et_micc2.utils.in_directory(self.context.project_path):
                            vs = toolinfo_git.version()
                            re_git_version = re.compile('^git version (\d+\.\d*\.\d*).*')
                            m = re_git_version.match(vs)
                            git_Mmp = m[1]
                            # print(git_Mmp)
                            if git_Mmp > '2.30':
                                cmds = [ ['git', 'init', f'--initial-branch={self.context.template_parameters["git_default_branch"]}']
                                       ]
                            else:
                                cmds = [ ['git', 'init']
                                       ]
                            cmds.extend(
                                    [ ['git', 'add', '*']
                                    , ['git', 'add', '.gitignore']
                                    , ['git', 'commit', '-m', '"And so this begun..."']
                                    ]
                            )

                            returncode = et_micc2.utils.execute(cmds, self.logger.debug, stop_on_error=True)
                    if not returncode:
                        if self.context.remote:
                            # todo this context manager does not print correctly
                            with et_micc2.logger.log(self.logger.info, f"Creating remote git repository at git://github.com/{github_username}/{self.context.project_path.name}"):
                                with et_micc2.utils.in_directory(self.context.project_path):
                                    pat_file = self.context._cfg_dir / f'{self.context.template_parameters["github_username"]}.pat'
                                    if pat_file.exists():
                                        with open(pat_file) as f:
                                            completed_process = \
                                                subprocess.run( ['gh', 'auth', 'login', '--with-token'], stdin=f, text=True )
                                            et_micc2.utils.log_completed_process(completed_process,self.logger.debug)

                                            cmds = [ ['gh', 'repo', 'create', self.context.project_path.name, f'--{self.context.remote}', '-y']
                                                   # next line is for accessing github via ssh
                                                   , ['git', 'remote', 'set-url', 'origin', f'git@github.com:{github_username}/{self.context.project_path.name}.git']
                                                   , ['git', 'push', '-u', 'origin', self.context.template_parameters['git_default_branch']]
                                                   ]
                                            et_micc2.utils.execute(cmds, self.logger.debug, stop_on_error=True)
                                    else:
                                        self.logger.error(
                                            f"Unable to access your GitHub account: \n"
                                            f"    Personal access token not found: '{pat_file}'.\n"
                                            f"Remote repository not created."
                                        )
                        else:
                            self.logger.warning("Creation of remote GitHub repository not requested.")

                # self.logger.warning(
                #     "Run 'poetry install' in the project directory to create a virtual "
                #     "environment and install its dependencies."
                # )

        if self.context.publish:
            self.logger.warning(
                f"The name '{self.context.package_name}' is still available on PyPI.\n"
                "To claim the name, it is best to publish your project right away\n"
                "by running 'poetry publish --build'."
            )


    @property
    def version(self):
        """Return the project's version (str)."""
        return self.pyproject_toml['tool']['poetry']['version']


    def info_cmd(self):
        """Output info on the project."""

        # This command does not require any external tools.

        if self.context.verbosity >= 0:
            self.context.verbosity = 10

        if self.context.verbosity >= 1:
            click.echo(
                "Project " + click.style(str(self.context.project_path.name), fg='green')
               + " located at " + click.style(str(self.context.project_path), fg='green')
               + "\n  package: " + click.style(str(self.context.package_name), fg='green')
               + "\n  version: " + click.style(self.version, fg='green')
            )

        if self.context.verbosity >= 3:
            click.echo("  contents:")
            lines = []
            top = self.context.project_path / self.context.package_name
            for d, dirs, files in os.walk(top):
                if '_cmake_build' in d:
                    continue
                pd = Path(d)
                submodule_type = get_submodule_type(pd)
                pdr = pd.relative_to(self.context.project_path)
                if pd == top:
                    tp = 'top-level package      (source in '
                    src = str(pdr / '__init__.py')
                else:
                    if submodule_type == 'py':
                        tp = f'Python submodule       (source in '
                        src = f'{pdr}/__init__.py'
                    elif submodule_type == 'f90':
                        tp = f'Fortran submodule      (source in '
                        src = f'{pdr}/{pdr.name}.f90'
                    elif submodule_type == 'cpp':
                        tp = f'C++ submodule          (source in '
                        src = f'{pdr}/{pdr.name}.cpp'
                    else:
                        continue
                lines.append((str(pdr), tp, src))
                if pd == top:
                    for file in files:
                        if file.startswith('cli_') and file.endswith('.py'):
                            lines.append((f'{pd.name}{os.sep}{file}', 'Command Line Interface', ''))
            w = 0
            for line in lines:
               w = max(w, len(line[0]))
            w += 2
            for line in lines:
                s = '    ' + str(line[0]).ljust(w)
                click.echo(
                    click.style(s, bold=True) +
                    click.style(line[1]) +
                    click.style(line[2], fg='green') +
                    (')' if line[2] else '')
                )


    def version_cmd(self):
        """Bump the version according to :py:obj:`self.context.rule` or show the
        current version if no rule is specified.

        The version is stored in pyproject.toml in the project directory, and in
        :py:obj:`__version__` variable of the top-level package, which is either
        in :file:`<package_name>.py`, :file:`<package_name>/__init__.py`, or in
        :file:`<package_name>/__version__.py`.
        """

        # This command does not require any external tools.

        self.context.verbosity = max(1, self.context.verbosity)

        if not self.context.rule:
            if self.context.short:
                print(self.version)
            else:
                click.echo("Project " + click.style(f"({self.context.project_path.name}) ", fg='green')
                           + "version " + click.style(f"({self.version}) ", fg='green')
                           )
        else:
            r = f"--{self.context.rule}"
            current_semver = semantic_version.Version(self.version)
            if self.context.rule == 'patch':
                new_semver = current_semver.next_patch()
            elif self.context.rule == 'minor':
                new_semver = current_semver.next_minor()
            elif self.context.rule == 'major':
                new_semver = current_semver.next_major()
            else:
                r = f"--rule {self.context.rule}"
                new_semver = semantic_version.Version(self.context.rule)

            # update pyproject.toml
            if not self.context.dry_run:
                self.pyproject_toml['tool']['poetry']['version'] = str(new_semver)
                self.pyproject_toml.save()
                # update __version__
                look_for = f'__version__ = "{current_semver}"'
                replace_with = f'__version__ = "{new_semver}"'
                # update in <package_name>/__init__.py
                p = self.context.project_path / self.context.package_name / "__version__.py"
                if p.exists():
                    et_micc2.utils.replace_in_file(p, look_for, replace_with)
                else:
                    p = self.context.project_path / self.context.package_name / '__init__.py'
                    et_micc2.utils.replace_in_file(p, look_for, replace_with)

                self.logger.info(f"({self.context.project_path.name})> version ({current_semver}) -> ({new_semver})")
            else:
                click.echo(f"({self.context.project_path.name})> micc version {r} --dry-run : "
                           + click.style(f"({current_semver} ", fg='cyan') + "-> "
                           + click.style(f"({new_semver})", fg='cyan')
                           )

    def tag_cmd(self):
        """Create and push a version tag ``v<Major>.<minor>.<patch>`` for the current version."""

        # Git is required

        git = ToolInfo('git')
        if not git.is_available():
            s = '(or not suitable) ' if on_vsc_cluster() else ''
            error(f'The tag command requires git, which is not available {s}in your environment.\n'
                        'Exiting.')

        tag = f"v{self.version}"

        with et_micc2.utils.in_directory(self.context.project_path):
            self.logger.info(f"Creating git tag {tag} for project {self.context.project_path.name}")
            cmd = ['git', 'tag', '-a', tag, '-m', f'"tag version {self.version}"']
            self.logger.debug(f"Running '{' '.join(cmd)}'")
            completed_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.logger.debug(completed_process.stdout.decode('utf-8'))
            if completed_process.stderr:
                self.logger.critical(completed_process.stderr.decode('utf-8'))

            self.logger.debug(f"Pushing tag {tag} for project {self.context.project_path.name}")
            cmd = ['git', 'push', 'origin', tag]
            self.logger.debug(f"Running '{' '.join(cmd)}'")
            completed_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if completed_process.returncode == 0:
                if completed_process.stdout:
                    self.logger.debug(completed_process.stdout.decode('utf-8'))
            else:
                if completed_process.stdout:
                    self.logger.warning(completed_process.stdout.decode('utf-8'))
                if completed_process.stderr:
                    self.logger.warning(completed_process.stderr.decode('utf-8'))
                self.logger.warning(f"Failed '{' '.join(cmd)}'\nRerun the command later (you must be online).")

        self.logger.info('Done.')


    def add_cmd(self):
        """Add some source file to the project.

        This method dispatches to

        * :py:meth:`add_python_cli`,
        * :py:meth:`add_python_submodule`,
        * :py:meth:`add_f90_module`,
        * :py:meth:`add_cpp_module`
        """
        # set implied flags:
        if self.context.flag_clisub: # cli with subcommands
            app_implied = f" [implied by --clisub   ({int(self.context.flag_clisub)})]"
            self.context.flag_cli = True
        else:
            app_implied = ""

        if self.context.flag_cli:
            # Prepare for adding a cli component
            cli = Cli(self.context)
            db_entry = cli.create()

        else:
            # Prepare for adding a submodule
            submodule = Submodule(self)
            db_entry = submodule.create()

        self.deserialize_db()
        self.serialize_db(db_entry)


    def build_cmd(self):
        """Build a binary extension."""

        # Exit if cmake is not available:
        if not ToolInfo('cmake').is_available():
            msg = 'The build command requires cmake, which is not available in your current environment.\n'
            if on_vsc_cluster():
                msg += 'Load a cluster module that enables cmake.'
            else:
                msg += 'Make sure cmake is installed and on your PATH.'
            error(msg)

        # get extension for binary extensions (depends on OS and python version)
        extension_suffix = get_extension_suffix()

        package_path = self.context.project_path / self.context.package_name

        build_options = self.context.build_options
        if build_options.module_to_build:
            build_options.module_to_build = package_path / build_options.module_to_build

        succeeded = []
        failed = []
        for root, dirs, files in os.walk(package_path):
            for dir in dirs:
                p_root = Path(root)
                submodule_type = get_submodule_type(p_root / dir)
                # print(root, dir,submodule_type)
                if submodule_type in ('f90','cpp'):
                    build = True
                    if build_options.module_to_build:
                        if build_options.module_to_build != p_root / dir:
                            build = False
                    if build:
                        if submodule_type == 'f90':
                            # Exit if f2py is not available
                            if not ToolInfo('f2py').is_available():
                                msg = 'Building a Fortran binary extension requires f2py, which is not available in your current environment.\n' \
                                      '(F2py is part of the numpy Python package).'
                                if on_vsc_cluster():
                                    msg += 'Load a cluster module that has the numpy package pre-installed.'
                                else:
                                    msg += 'If you are using a virtual environment, install numpy as:\n' \
                                           '    (.venv) > pip install numpy\n' \
                                           'otherwise,\n' \
                                           '    > pip install numpy --user\n'
                                error(msg)
                        elif submodule_type == 'cpp':
                            # exit if pybind11 is not available, and warn if too old...
                            pybind11 = PkgInfo('pybind11')
                            if not pybind11.is_available():
                                error(
                                    'Building C++ binary extensions requires pybind11, which is not available in your current environment.\n'
                                    'If you are using a virtual environment, install it as .\n'
                                    '    (.venv) > pip install pybind11\n'
                                    'otherwise,\n'
                                    '    > pip install pybind11 --user\n'
                                    , exit_code=_exit_missing_component
                                    )
                            else:
                                if pybind11.version() < __pybind11_required_version__:
                                    warning(
                                        f'Building C++ binary extensions requires pybind11, which is available in your current environment (v{pybind11.version()}).\n'
                                        f'However, you may experience problems because it is older than v{__pybind11_required_version__}.\n'
                                        'Upgrading is recommended.'
                                    )

                        build_options.submodule_srcdir_path = build_options.module_to_build if build_options.module_to_build else (p_root / dir)
                        build_options.submodule_path        = build_options.submodule_srcdir_path.parent
                        build_options.submodule_name        = build_options.submodule_srcdir_path.name
                        build_options.submodule_binary      = build_options.submodule_path / (build_options.submodule_name + extension_suffix)
                        build_options.submodule_type = submodule_type

                        if build_binary_extension(self.context):
                            failed.append(build_options.submodule_binary)
                        else:
                            succeeded.append(build_options.submodule_binary)

        if succeeded:
            self.logger.info("\n\nBinary extensions built successfully:")
            for binary_extension in succeeded:
                self.logger.info(f"  - {binary_extension}")

        if failed:
            self.logger.error("\nBinary extensions failing to build:")
            for binary_extension in failed:
                self.logger.error(f"  - {binary_extension}")

        if not succeeded and not failed:
            warning(f"No binary extensions found in package ({self.context.package_name}).")


    def get_logger(self, log_file_path=None):
        """"""
        if self.logger:
            return

        if log_file_path:
            log_file_name = log_file_path.name
            log_file_dir = log_file_path.parent
        else:
            log_file_name = f"{self.context.project_path.name}.micc.log"
            log_file_dir = self.context.project_path
            log_file_path = log_file_dir / log_file_name
        self.log_file = log_file_path

        if getattr(self.context, 'clear_log', False):
            if log_file_path.exists():
                log_file_path.unlink()

        # create a new logger object that will write to the log file and to the console
        self.logger = et_micc2.logger.create_logger(log_file_path)

        # set the log level from the verbosity
        self.logger.console_handler.setLevel(et_micc2.logger.verbosity_to_loglevel(self.context.verbosity))

        if self.context.verbosity > 2:
            print(f"Current logfile = {log_file_path}")

        if getattr(self.context, 'clear_log', False):
            self.logger.info(f"The log file was cleared: {log_file_path}")
            self.context.clear_log = False

        self.context.logger = self.logger


    def deserialize_db(self):
        """Read file ``db.json`` into self.db."""

        db_json = self.context.project_path / 'db.json'
        if db_json.exists():
            with db_json.open('r') as f:
                self.db = json.load(f)
        else:
            self.db = {}


    def serialize_db(self, db_entry=None, verbose=False):
        """Write self.db to file ``db.json``.

        Self.context is a SimpleNamespace object which is not default json serializable.
        This function takes care of that by converting to ``str`` where possible, and
        ignoring objects that do not need serialization, as e.g. self.context.logger.
        """

        if db_entry:
            # produce a json serializable version of db_entry['context']:
            my_options = {}
            for key, val in db_entry['context'].__dict__.items():
                if isinstance(val,(dict, list, tuple, str, int, float, bool)):
                    # default serializable types
                    my_options[key] = val
                    if verbose:
                        print(f"serialize_db: using ({key}:{val})")
                elif isinstance(val, Path):
                    my_options[key] = str(val)
                    if verbose:
                        print(f"serialize_db: using ({key}:str('{val}'))")
                else:
                    if verbose:
                        print(f"serialize_db: ignoring ({key}:{val})")

            db_entry['context'] = my_options

            if not hasattr(self, 'db'):
                # Read db.json into self.db if self.db does not yet exist.
                self.deserialize_db()

            # store the entry in self.db:
            self.db[self.context.add_name] = db_entry

        # finally, serialize self.db
        with et_micc2.utils.in_directory(self.context.project_path):
            with open('db.json','w') as f:
                json.dump(self.db, f, indent=2)


    def mv_component(self):
        """Rename or Remove a component (submodule, sub-package, Fortran module, C++ module, app (CLI)."""
        cur_name, new_name = self.context.cur_name, self.context.new_name
        # Look up <cur_name> in the project's database to find out what kind of a component it is:
        self.deserialize_db()
        db_entry = self.db[cur_name] # may raise KeyError

        component_options = db_entry['context']
        if new_name: # rename
            with et_micc2.logger.log(self.logger.info
                                   , f"Package '{self.context.package_name}' Renaming component {cur_name} -> {new_name}:"
                                   ):
                if self.context.entire_project:
                    self.logger.info(f"Renaming entire project (--entire-project): '{self.context.project_path.name}'")
                    self.replace_in_folder(self.context.project_path, cur_name, new_name)

                elif self.context.entire_package:
                    self.logger.info(f"Renaming entire package (--entire-package): '{self.context.package_name}'")
                    self.replace_in_folder(self.context.project_path / self.context.package_name, cur_name, new_name)

                elif component_options['package']:
                    self.logger.info(f"Renaming Python sub-package: '{cur_name}{os.sep}__init__.py'")
                    self.replace_in_folder(self.context.project_path / self.context.package_name / cur_name, cur_name, new_name)
                    self.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / 'tests' / f'test_{cur_name}.py', cur_name, new_name)

                elif component_options['py']:
                    self.logger.info(f"Renaming Python submodule: '{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / self.context.package_name / f'{cur_name}.py', cur_name, new_name)
                    self.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / 'tests' / f'test_{cur_name}.py', cur_name, new_name)

                elif component_options['f90']:
                    self.logger.info(f"Fortran submodule: 'f90_{cur_name}{os.sep}{cur_name}.f90'")
                    self.replace_in_folder(self.context.project_path / self.context.package_name / f'f90_{cur_name}', cur_name, new_name)
                    self.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / 'tests'/ f'test_f90_{cur_name}.py', cur_name, new_name)

                elif component_options['cpp']:
                    self.logger.info(f"C++ submodule: 'cpp_{cur_name}{os.sep}{cur_name}.cpp'")
                    self.replace_in_folder(self.context.project_path / self.context.package_name / f'cpp_{cur_name}', cur_name, new_name)
                    self.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / 'tests' / f'test_cpp_{cur_name}.py', cur_name, new_name)

                elif component_options['app'] or component_options['group']:
                    self.logger.info(f"Command line interface (no subcommands): 'cli_{cur_name}.py'")
                    self.replace_in_file(self.context.project_path / self.context.package_name / f"cli_{cur_name}.py", cur_name, new_name)
                    self.replace_in_file(self.context.project_path / 'tests' / f"test_cli_{cur_name}.py", cur_name, new_name)
                    
                for key,val in db_entry.items():
                    if not key=='context':
                        filepath = self.context.project_path / key
                        new_string = val.replace(cur_name, new_name)
                        self.replace_in_file(filepath, val, new_string, contents_only=True)
                        db_entry[key] = new_string

                # Update the database:
                self.logger.info(f"Updating database entry for : '{cur_name}'")
                self.db[new_name] = db_entry

        else: # remove
            with et_micc2.logger.log(self.logger.info
                                   , f"Package '{self.context.package_name}' Removing component '{cur_name}'"
                                   ):
                if component_options['package']:
                    self.logger.info(f"Removing Python sub-package: '{cur_name}{os.sep}__init__.py'")
                    self.remove_folder(self.context.project_path / self.context.package_name / cur_name)
                    self.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                    self.remove_file(self.context.project_path / 'tests' / f'test_{cur_name}.py',)

                elif component_options['py']:
                    self.logger.info(f"Removing Python submodule: '{cur_name}.py'")
                    self.remove_file(self.context.project_path / self.context.package_name / f'{cur_name}.py')
                    self.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                    self.remove_file(self.context.project_path / 'tests' / f'test_{cur_name}.py')

                elif component_options['f90']:
                    self.logger.info(f"Removing Fortran submodule: 'f90_{cur_name}")
                    self.remove_folder(self.context.project_path / self.context.package_name / f'f90_{cur_name}')
                    self.logger.info(f"Removing test file: 'tests/test_f90_{cur_name}.py'")
                    self.remove_file(self.context.project_path / 'tests' / f'test_f90_{cur_name}.py')

                elif component_options['cpp']:
                    self.logger.info(f"Removing C++ submodule: 'cpp_{cur_name}")
                    self.remove_folder(self.context.project_path / self.context.package_name / f'cpp_{cur_name}')
                    self.logger.info(f"Removing test file: 'tests/test_cpp_{cur_name}.py'")
                    self.remove_file(self.context.project_path / 'tests' / f'test_cpp_{cur_name}.py')

                elif component_options['cli'] or component_options['clisub']:
                    self.logger.info(f"Removing CLI: 'cli_{cur_name}.py'")
                    self.remove_file(self.context.project_path / self.context.package_name / f"cli_{cur_name}.py")
                    self.logger.info(f"Removing test file: 'test_cli_{cur_name}.py'")
                    self.remove_file(self.context.project_path /  'tests' / f"test_cli_{cur_name}.py")


                for key, val in db_entry.items():
                    if not key == 'context':
                        path = self.context.project_path / key
                        parent_folder, filename, old_string = path.parent, path.name, val
                        new_string = ''
                        self.replace_in_file(path, old_string, new_string, contents_only=True)

                # Update the database:
                self.logger.info(f"Updating database entry for : '{cur_name}'")

        del self.db[cur_name]
        self.serialize_db()


    def replace_in_folder( self, folderpath, cur_name, new_name ):
        """"""
        cur_dirname = folderpath.name
        new_dirname = cur_dirname.replace(cur_name,new_name)

        with et_micc2.logger.log(self.logger.info, f'Renaming folder "{cur_dirname}" -> "{new_dirname}"'):
            # first rename the folder
            new_folderpath = folderpath.parent / new_dirname
            os.rename(folderpath, new_folderpath)

            # rename subfolder names:
            folder_list = [] # list of tuples with (oldname,newname)
            for root, folders, files in os.walk(str(new_folderpath)):
                _filter(folders) # in place modification of the list of folders to traverse
                for folder in folders:
                    new_folder = folder.replace(cur_name,new_name)
                    folder_list.append((os.path.join(root,folder), os.path.join(root,new_folder)))

            # rename subfolder names:
            for tpl in folder_list:
                old_folder = tpl[0]
                new_folder = tpl[1]
                self.logger.info(f"Renaming folder '{old_folder}'  -> '{new_folder}'")
                os.rename(old_folder, new_folder)

            # rename in files and file contents:
            for root, folders, files in os.walk(str(new_folderpath)):
                for file in files:
                    if file.startswith('.orig.'):
                        continue
                    if file.endswith('.so'):
                        continue
                    if file.endswith('.json'):
                        continue
                    if file.endswith('.lock'):
                        continue
                    self.replace_in_file(Path(root) / file, cur_name, new_name)
                _filter(folders) # in place modification of the list of folders to traverse


    def remove_file(self,path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


    def remove_folder(self,path):
        shutil.rmtree(path)


    def replace_in_file(self, filepath, cur_name, new_name, contents_only=False):
        """Replace <cur_name> with <new_name> in the filename and its contents."""

        file = filepath.name

        what = 'Modifying' if contents_only else 'Renaming'
        with et_micc2.logger.log(self.logger.info, f"{what} file {filepath}:"):
            self.logger.info(f'Reading from {filepath}')
            with open(filepath,'r') as f:
                old_contents = f.read()

            self.logger.info(f'Replacing "{cur_name}" with "{new_name}" in file contents.')
            new_contents = old_contents.replace(cur_name, new_name)

            if contents_only:
                new_file = file
            else:
                new_file = file.replace(cur_name,new_name)
                self.logger.info(f'Replacing "{cur_name}" with "{new_name}" in file name -> "{new_file}"')
            new_path = filepath.parent / new_file

            # By first renaming the original file, we avoid problems when the new
            # file name is identical to the old file name (because it is invariant,
            # e.g. __init__.py)
            orig_file = '.orig.'+file
            orig_path = filepath.parent / orig_file
            self.logger.info(f'Keeping original file "{file}" as "{orig_file}".')
            os.rename(filepath, orig_path)

            self.logger.info(f'Writing modified file contents to {new_path}: ')
            with open(new_path,'w') as f:
                f.write(new_contents)

    
    def doc_cmd(self):
        """Build documentation."""

        if on_vsc_cluster():
            error("The cluster is not suited for building documentation. Use a desktop machine instead.")

        # Check needed tools
        if not ToolInfo('make').is_available():
            error("The make command is missing in your current environment. You must install it to build documentation.")
        if not PkgInfo('sphinx').is_available():
            error("The sphinx package is missing in your current environment.\n"
                       "You must install it to build documentation.")
        if not PkgInfo('sphinx_rtd_theme').is_available():
            error("The sphinx_rtd_theme package is missing in your current environment.\n"
                       "You must install it to build documentation.")
        if not PkgInfo('sphinx_click').is_available():
            error("The sphinx_click package is missing in your current environment.\n"
                       "You must install it to build documentation.")

        exit_code = et_micc2.utils.execute(
            ['make', self.context.what],
            cwd=Path(self.context.project_path) / 'docs',
            logfun=self.logger.info
        )
        if exit_code:
            error('unexpected error')


    # def venv_cmd(self):
    #     """"""
    #     venv_path = self.context.project_path / self.context.venv_name
    #     if venv_path.exists():
    #         error(f'A virtual environment with name `{venv_path}` exists already.\n'
    #                    f'Choose another name, or delete it first.')
    # 
    #     if not Path(self.context.python_executable).exists():
    #         error(f'The Python executable `{self.context.python_executable}` is not found.')
    # 
    #     cmd = [self.context.python_executable, '-m', 'venv', self.context.venv_name]
    #     if self.context.system_site_packages:
    #         cmd.append('--system-site-packages')
    #     self.exit_code = et_micc2.utils.execute(cmd, cwd=self.context.project_path, logfun=self.logger.info)


def get_extension_suffix():
    """Return the extension suffix, e.g. :file:`.cpython-37m-darwin.so`."""
    return sysconfig.get_config_var('EXT_SUFFIX')


def build_binary_extension(context):
    """Build a binary extension described by *context*.

    :param context:
    :return:
    """
    build_options = context.build_options
    # self.context.build_options.submodule_srcdir_path = build_options.module_to_build
    # self.context.build_options.submodule_path = build_options.module_to_build.parent
    # self.context.build_options.submodule_name = build_options.module_to_build.name
    # self.context.build_options.submodule_binary = build_options.module_to_build.parent / (
    #             build_options.module_to_build.name + extension_suffix)
    # self.context.build_options.submodule_type = submodule_type

    # Remove so file to avoid "RuntimeError: Symlink loop from ..."
    try:
        build_options.submodule_binary.unlink()  # missing_ok=True only available from 3.8 on, not in 3.7
    except FileNotFoundError:
        pass
    module_to_build = build_options.submodule_srcdir_path.relative_to(context.project_path)
    build_log_file = build_options.submodule_srcdir_path / "micc-build.log"
    build_logger = et_micc2.logger.create_logger(build_log_file, filemode='w')
    with et_micc2.logger.log(build_logger.info, f"Building {build_options.submodule_type} module '{module_to_build}':"):
        destination = build_options.submodule_binary

        if build_options.submodule_type in ('cpp', 'f90') and (build_options.submodule_srcdir_path / 'CMakeLists.txt').is_file():
            output_dir = build_options.submodule_srcdir_path / '_cmake_build'
            # build_dir = output_dir
            if build_options.clean and output_dir.exists():
                build_logger.info(f"--clean: shutil.removing('{output_dir}').")
                shutil.rmtree(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            with et_micc2.utils.in_directory(output_dir):
                cmake_cmd = ['cmake', '-D', f"PYTHON_EXECUTABLE={sys.executable}"]
                # CAVEAT: using sys.executable implies that we automatically build against the python version used
                #         by micc2. This is not always what we want.
                for key,val in context.build_options.cmake.items():
                    cmake_cmd.extend(['-D', f"{key}={val}"])
                if sys.platform == 'win32':
                    cmake_cmd.extend(['-G', 'NMake Makefiles'])
                    make = 'nmake'
                else:
                    make = 'make'

                if build_options.submodule_type== 'cpp':
                    cmake_cmd.extend(['-D', f"pybind11_DIR={path_to_cmake_tools()}"])

                cmake_cmd.append('..')

                cmds = [ cmake_cmd
                       , [make, 'VERBOSE=1']
                       # [make, 'install']
                ]
                # This is a fix for the native Windows case, when using the
                # Intel Python distribution and building a f90 binary extension
                fix = sys.platform == 'win32' and 'intel' in sys.executable and context.module_kind == 'f90'
                if not fix:
                    cmds.append([make, 'install'])

                exit_code = et_micc2.utils.execute(
                    cmds, build_logger.debug, stop_on_error=True, env=os.environ.copy()
                )

                if fix:
                    from glob import glob
                    search = str(build_options.submodule_srcdir_path / '_cmake_build' / f'{context.module_name}.*.pyd')
                    # print(search)
                    pyd = glob(search)
                    dst = build_options.submodule_binary.parent / f'{build_options.submodule_name}.pyd'
                    build_logger.info(f'Installing `{pyd[0]}` as {dst}')
                    shutil.copyfile(pyd[0], dst)

                if build_options.cleanup:
                    build_logger.info(f"--cleanup: shutil.removing('{output_dir}').")
                    shutil.rmtree(build_dir)
        else:
            raise RuntimeError("Bad submodule type, or no CMakeLists.txt   ")

    return exit_code


def path_to_cmake_tools():
    """Return the path to the folder with the CMake tools.
    
    """
    found = ''
    #look in global site-packages:
    site_packages = site.getsitepackages()
    site_packages.append(site.getusersitepackages())
    print(site_packages)
    for d in site_packages:
        pd = Path(d) / 'pybind11'
        if pd.exists():
            found = pd
            break
    
    if not found:
        raise ModuleNotFoundError('pybind11 not found in {site_packages}')
        
    p = pd / 'share' / 'cmake' / 'pybind11'
    print(f'path_to_cmake_tools={p}')
    return str(p)


def _filter(folders):
    """"In place modification of the list of folders to traverse.

    see https://docs.python.org/3/library/os.html

    ...

    When topdown is True, the caller can modify the dirnames list in-place
    (perhaps using del or slice assignment), and walk() will only recurse
    into the subdirectories whose names remain in dirnames; this can be used
    to prune the search, impose a specific order of visiting, or even to
    inform walk() about directories the caller creates or renames before it
    resumes walk() again. Modifying dirnames when topdown is False has no
    effect on the behavior of the walk, because in bottom-up mode the
    directories in dirnames are generated before dirpath itself is generated.

    ...
    """
    exclude_folders = ['.venv', '.git', '_build', '_cmake_build', '__pycache__']
    folders[:] = [f for f in folders if not f in exclude_folders]

def auto_build_binary_extension(package_path, module_to_build):
    """

    :param Path package_path:
    :param str module_to_build:
    :return: exit_code
    """
    options = SimpleNamespace( package_path  = package_path
                             , verbosity     = 1
                             , module_name   = module_to_build
                             , build_options = SimpleNamespace( module_to_build = module_to_build
                                                              , clean           = True
                                                              , cleanup         = True
                                                              , cmake           = {'CMAKE_BUILD_TYPE': 'RELEASE'}
                                                              )
                             )
    for module_prefix in ["cpp", "f90"]:
        module_srcdir_path = package_path / f"{module_prefix}_{context.module_name}"
        if module_srcdir_path.exists():
            context.module_kind = module_prefix
            context.module_srcdir_path = module_srcdir_path
            context.build_options.build_tool_options = {}
            break
    else:
        raise ValueError(f"No binary extension source directory found for module '{module_to_build}'.")

    exit_code = build_binary_extension(options)

    msg = ("[ERROR]\n"
          F"    Binary extension module '{context.module_name}{get_extension_suffix()}' could not be build.\n"
           "    Any attempt to use it will raise exceptions.\n"
           ) if exit_code else ""
    return msg


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
        self.context.module_srcdir = os.path.join(self.context.package_name, p_add_name)
        self.context.import_lib = self.context.module_srcdir.replace(os.sep,".")
        self.context.template_parameters.update(
            { 'module_name': self.context.module_name
            , 'source_dir' : self.context.module_srcdir
            , 'import_lib' : self.context.import_lib
            }
        )

        # Verify that the module_name is not already used:
        if (self.context.project_path / self.context.package_name / self.context.module_location_relative / self.context.module_name).is_dir():
            error(f"Project {self.context.project_path.name} has already a module named {self.context.import_lib}.")

        # Verify that the name is valid:
        pep8_module_name = et_micc2.utils.pep8_module_name(self.context.module_name)
        if (not et_micc2.utils.verify_project_name(self.context.module_name)
            or self.context.module_name != pep8_module_name
           ):
            suggest = f'Suggesting: "{pep8_module_name}".' if et_micc2.utils.verify_project_name(pep8_module_name) else ''
            error(
                f"Not a valid module name ({self.context.module_name}). Valid names:\n"
                f"  * start with a letter [a-z]\n"
                f"  * contain only lowercase letters [a-z], digits, and underscores\n"
                f"{suggest}"
            )

        # Verify theat the parent is a python package
        parent = self.context.project_path / self.context.package_name / self.context.module_location_relative
        if not (parent / '__init__.py').is_file():
            error(
                f"The parent of a submodule must be a python package.\n"
                f"    {parent} is not a Python package."
            )


    def create(self):
        """Create the submodule
        """
        db_entry = {'context': self.context}

        if self.context.flag_py:
            # prepare for adding a Python submodule:
            self.context.templates = ['submodule-py', 'submodule-py-test']
            self.add_python_submodule(db_entry)

        else: # add a binary extension module
            # Warn if cmake is not available
            if not ToolInfo('cmake').is_available():
                warning('Building binary extensions requires cmake, which is currently not available in your environment.')

            if self.context.flag_f90:
                # Warn if f2py is not available
                if not ToolInfo('f2py').is_available():
                    msg = 'Building Fortran binary extensions requires f2py, which is currently not available in your environment.\n'
                    if on_vsc_cluster():
                        msg += 'To enable f2py:\n'\
                               '    load a cluster module that has numpy pre-installed.\n'
                    else:
                        msg += 'To enable f2py, install numpy:\n' \
                               '    If you are using a virtual environment:\n' \
                               '            (.venv) > pip install numpy\n' \
                               '    otherwise:\n' \
                               '            > pip install numpy --user\n'
                    msg += '(You also need a Fortran compiler and a C compiler).'
                    warning(msg)

                # prepare for adding a Fortran submodule:
                self.context.templates = ['submodule-f90', 'submodule-f90-test']
                self.add_f90_submodule(db_entry)

            if self.context.flag_cpp:
                # Warn if pybind11 is not available or too old
                pybind11 = PkgInfo('pybind11')
                if not pybind11.is_available():
                    warning('Building C++ binary extensions requires pybind11, which is not available in your environment.\n'
                                 'If you are using a virtual environment, install it as .\n'
                                 '    (.venv) > pip install pybind11\n'
                                 'otherwise,\n'
                                 '    > pip install pybind11 --user\n'
                                 '(You also need a C++ compiler).'
                                 )
                else:
                    if pybind11.version() < __pybind11_required_version__:
                        warning(f'Building C++ binary extensions requires pybind11, which is available in your environment (v{pybind11.version()}).\n'
                                     f'However, you may experience problems because it is older than v{__pybind11_required_version__}.\n'
                                      'Upgrading is recommended.'
                                     )

                # prepare for adding a C++ submodule:
                self.context.templates = ['submodule-cpp', 'submodule-cpp-test']
                self.add_cpp_submodule(db_entry)

        return db_entry


    def add_python_submodule(self, db_entry):
        """

        :param dbentry:
        """
        with et_micc2.logger.log(self.logger.info,
                                f"Adding python submodule {self.context.add_name} to package {self.context.package_name}."
                                ):

            # Create the needed folders and files by expanding the templates:
            msg = et_micc2.expand.expand_templates(self.context)
            if msg:
                self.logger.critical(msg)
                return

            src_file = self.context.project_path / self.context.package_name / self.context.add_name / '__init__.py'
            tst_file = self.context.project_path / 'tests' / self.context.package_name / self.context.add_name / f'test_{self.context.module_name}.py'

            self.logger.info(f"- python source in    {src_file}.")
            self.logger.info(f"- Python test code in {tst_file}.")

            with et_micc2.utils.in_directory(self.context.project_path):
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
        with et_micc2.logger.log(self.logger.info,
                                f"Adding f90 submodule {self.context.add_name} to package {self.context.package_name}."
                                ):

            # Create the needed folders and files by expanding the templates:
            msg = et_micc2.expand.expand_templates(self.context)
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

            with et_micc2.utils.in_directory(self.context.project_path):
                # docs
                filename = "API.rst"
                text = f"\n.. include:: ../{self.context.package_name}/{self.context.module_location_relative}/{self.context.module_name}.rst\n"
                with open(filename, "a") as f:
                    f.write(text)
                db_entry[filename] = text

        self.add_auto_build_code(db_entry)

    def add_auto_build_code(self, db_entry):
        """Add auto build code for binary extension modules in :file:`__init__.py` of the package."""
        module_name = self.context.add_name
        import_lib = self.context.import_lib
        text_to_insert = [
            "",
            "try:",
            f"    import {import_lib}",
            "except ModuleNotFoundError as e:",
            "    # Try to build this binary extension:",
            "    from pathlib import Path",
            "    import click",
            "    from et_micc2.project import auto_build_binary_extension",
            f"    msg = auto_build_binary_extension(Path(__file__).parent, '{module_name}')",
            "    if not msg:",
            f"        import {import_lib}",
            "    else:",
            f"        click.secho(msg, fg='bright_red')",
        ]
        file = os.path.join(self.context.package_name, '__init__.py')
        et_micc2.utils.insert_in_file(
            self.context.project_path / file,
            text_to_insert,
            startswith="__version__ = ",
        )
        text = '\n'.join(text_to_insert)
        db_entry[file] = text

    def add_cpp_submodule(self, db_entry):
        """Add a cpp module to this project."""
        with et_micc2.logger.log(self.logger.info,
                                f"Adding cpp submodule {self.context.add_name} to package {self.context.package_name}."
                                ):
            msg = et_micc2.expand.expand_templates(self.context)
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

            with et_micc2.utils.in_directory(self.context.project_path):
                # docs
                with open("API.rst", "a") as f:
                    filename = "API.rst"
                    text = f"\n.. include:: ../{self.context.package_name}/{self.context.module_location_relative}/{self.context.module_name}.rst\n"
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
        et_micc2.utils.insert_in_file(
            self.context.project_path / file,
            text_to_insert,
            startswith="__version__ = ",
        )
        text = '\n'.join(text_to_insert)
        db_entry[file] = text


def get_submodule_type(path):
    """Find out the type of a submodule.  
    
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
    def __init__(self,context):
        self.context = context
        app_name = self.context.add_name
        if os.sep in app_name:
            error("CLIs must be located in the package directory. They cannot be path-like.")

        if (context.project_path / context.package_name / f"cli_{app_name}.py").is_file():
            error(f"Project {self.context.project_path.name} has already an app named {app_name}.")

        if not et_micc2.utils.verify_project_name(app_name):
            error(
                f"Not a valid app name ({app_name}_. Valid names:\n"
                f"  * start with a letter [a-zA-Z]\n"
                f"  * contain only [a-zA-Z], digits, hyphens, and underscores\n"
            )

    def create(self):
        """Add a console script (app, aka CLI) to the package."""
        db_entry = {'context': self.context}

        if self.context.flag_clisub:
            self.context.templates = ['app-sub-commands']
        else:
            self.context.templates = ['app-single-command']

        app_name = self.context.add_name
        cli_app_name = 'cli_' + et_micc2.utils.pep8_module_name(app_name)
        cli_type = '(CLI with subcommands)' if self.context.flag_clisub else '(single command CLI)'

        with et_micc2.logger.log( self.context.logger.info
                                , f"Adding CLI {app_name} to project {self.context.project_path.name}\n"
                                  f"    {cli_type}."
                                ):
            self.context.template_parameters.update(
                { 'app_name': app_name
                , 'cli_app_name': cli_app_name
                }
            )

            msg = et_micc2.expand.expand_templates(self.context)
            if msg:
                self.logger.critical(msg)
                return

            package_name = self.context.template_parameters['package_name']
            src_file = os.path.join(self.context.project_path.name, package_name, f"cli_{app_name}.py")
            tst_file = os.path.join(self.context.project_path.name, 'tests', f"test_cli_{app_name}.py")
            self.context.logger.info(f"- Python source file {src_file}.")
            self.context.logger.info(f"- Python test code   {tst_file}.")

            with et_micc2.utils.in_directory(self.context.project_path):
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
                txt2 = (f".. click:: {package_name}.{cli_app_name}:main\n"
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
                db_entry['pyproject.toml'] = f'{app_name} = "refactoring_dev:cli_{app_name}.main"\n'

                # add 'import <package_name>.cli_<app_name> to __init__.py
                line = f"import {package_name}.cli_{app_name}\n"
                file = self.context.project_path / self.context.package_name / '__init__.py'
                et_micc2.utils.insert_in_file(file, [line], before=True, startswith="__version__")
                db_entry[os.path.join(self.context.package_name, '__init__.py')] = line

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
            range1 = et_micc2.utils.version_range(version_constraint)
            range2 = et_micc2.utils.version_range(tool_poetry_dependencies[pkg])
            if range1 == range2:
                # nothing to do: new and old version specifcation are the same
                continue
            intersection = et_micc2.utils.intersect(range1, range2)
            if et_micc2.utils.validate_intersection(intersection):
                range = intersection
            else:
                range = et_micc2.utils.most_recent(version_constraint, tool_poetry_dependencies[pkg])
            tool_poetry_dependencies[pkg] = et_micc2.utils.version_constraint(range)
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

# eof
