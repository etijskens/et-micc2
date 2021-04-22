# -*- coding: utf-8 -*-

"""
Application micc2
"""

def sys_path_helper():
    """Make sure that et_micc2 can be imported in case this file is executed as::

            (.venv)> python et_micc2/cli_micc.py <args>
    """
    try:
        import et_micc2
    except ModuleNotFoundError:
        p = Path(__file__) / '..' / '..'
        sys.path.insert(0, str(p.resolve()))


import os, sys, shutil
from types import SimpleNamespace
from pathlib import Path

import click

sys_path_helper()
from et_micc2.project import Project, micc_version
import et_micc2.logger
import et_micc2.config

if '3.8' < sys.version:
    from et_micc2.check_environment import check_cmd

__template_help = "Ordered list of Cookiecutter templates, or a single Cookiecutter template."


def underscore2space(text):
    return text.replace('_', ' ')

__subcmds_supporting_overwrite_preferences__ = ('setup', 'create')
__cfg_filename__ = 'micc2.cfg'
__cfg_dir__ = Path.home() / '.micc2'

####################################################################################################
# main
####################################################################################################
@click.group()
@click.option('-v', '--verbosity', count=True
    , help="The verbosity of the program output."
    , default=1
)
@click.option('-p', '--project-path'
    , help="The path to the project directory. "
           "The default is the current working directory."
    , default='.'
    , type=str
)
@click.option('--clear-log'
    , help="If specified clears the project's ``et_micc2.log`` file."
    , default=False, is_flag=True
)
# optionally overwrite preferences (supporting sub-commands only):
@click.option('--full-name'
    , help=f"Overwrite preference `full_name`, use underscores for spaces. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--email'
    , help=f"Overwrite preference `email`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--github-username'
    , help=f"Overwrite preference `github_username`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--sphinx-html-theme'
    , help=f"Overwrite preference `sphinx_html_theme`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--software-license'
    , help=f"Overwrite preference `software_license`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--git-default-branch'
    , help=f"Overwrite preference `git_default_branch`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
@click.option('--minimal_python_version'
    , help=f"Overwrite preference `minimal_python_version`. (supporting sub-commands only {__subcmds_supporting_overwrite_preferences__})"
    , default=''
)
# end of preferences overwrite options
# Don't put any options below, otherwise they will be treated as overwrite preferences.
@click.version_option(version=micc_version())
@click.pass_context
def main( ctx, verbosity, project_path, clear_log
        , **overwrite_preferences
        ):
    """Micc2 command line interface.

    All commands that change the state of the project produce some output that
    is send to the console (taking verbosity into account). It is also sent to
    a logfile ``et_micc2.log`` in the project directory. All output is always appended
    to the logfile. If you think the file has gotten too big, or you are no more
    interested in the history of your project, you can specify the ``--clear-log``
    flag to clear the logfile before any command is executed. In this way the
    command you execute is logged to an empty logfile.

    See below for (sub)commands.
    """
    if verbosity > 1:
        print(f"micc2 ({et_micc2.__version__}) using Python", sys.version.replace('\n', ' '), end='\n\n')

    if clear_log:
        os.remove(project_path / 'micc.log')

    ctx.obj = SimpleNamespace(
        verbosity=verbosity,
        project_path=Path(project_path).resolve(),
        default_project_path=(project_path=='.'),
        clear_log=clear_log,
        __cfg_filename__=__cfg_filename__,
        __cfg_dir__=__cfg_dir__
    )

    overwrite_preferences_set = {}
    if ctx.invoked_subcommand in __subcmds_supporting_overwrite_preferences__:
        # Remove overwrite_preferences which have not been explicitly set:
        for key,value in overwrite_preferences.items():
            if value:
                overwrite_preferences_set[key] = value
    else:
        for key, value in overwrite_preferences.items():
            if value:
                print(f'Warning: overwriting preferences is supported only for subcommands `setup` and `create`.\n'
                      f'         Ignoring `{key}={value}`.')

    try:
        preferences = et_micc2.config.Config(file_loc=ctx.obj.project_path / __cfg_filename__)
    except FileNotFoundError:
        try:
            preferences = et_micc2.config.Config(file_loc=__cfg_dir__ / __cfg_filename__)
        except FileNotFoundError:
            preferences = None
    
    if preferences is None:
        # no preferences file found
        if ctx.invoked_subcommand == 'setup':
            # we're about to create one.
            pass
        else:
            # other commands cannot be executed without a preferences file:
            print(f"ERROR: No configuration file found in \n"
                  f"       - {ctx.obj.project_path / 'micc2.cfg'}\n"
                  f"       - {Path.home() / '.et-micc2/.et-micc2.cfg'}\n"
                  f"Run `micc setup` first.")
            ctx.exit(1)

    # pass on the preferences and their overwrites to the subcommands (The overwrite_preferences
    # are empty if the invoked subcommands do not support it
    ctx.obj.preferences = preferences
    ctx.obj.overwrite_preferences = overwrite_preferences_set


####################################################################################################
# setup
####################################################################################################
@main.command()
@click.option('--force', '-f', is_flag=True
    , help="Overwrite existing setup."
    , default=False
              )
@click.pass_context
def setup(ctx
          , force
          ):
    """Setup your micc preferences.

    This command must be run once before you can use micc to manage your projects.
    """
    options = ctx.obj

    if not options.preferences is None:
        if force:
            click.secho(f"Overwriting earlier setup: \n    {options.preferences['file_loc']}", fg='bright_red')
            click.secho("Enter a suffix for the configuration directory if you want to make a backup.")
            while 1:
                suffix = input(':> ')

                if suffix:  # make backup
                    p_cfg_dir = Path(options.preferences['file_loc']).parent
                    p_cfg_dir_renamed = p_cfg_dir.parent / (p_cfg_dir.name + suffix)
                    if p_cfg_dir_renamed.exists():
                        click.secho(f'Error: suffix `{suffix}` is already in use, choose anoher.', fg='bright_red')
                    else:
                        p_cfg_dir.rename(p_cfg_dir_renamed)
                        break
            # forget the previous preferences.
            options.preferences = None
        else:
            print(f"Micc2 has already been set up:\n"
                  f"    {options.preferences['file_loc']}\n"
                  f"Use '--force' or '-f' to overwrite the existing preferences file.")
            ctx.exit(1)

    preferences_setup = { "full_name"        : { "text": "your full name"
                                               , "postprocess": underscore2space
                                               }
                        , "email"            : {"text": "your e-mail address"
                                               }
                        , "github_username"  : {"default": ""
                                               , "text": "your github username (leave empty if you do not have one,\n"
                                                         "  or create one first at https://github.com/join)"
                                               }
                        , "sphinx_html_theme": {"default": "sphinx_rtd_theme",
                                                "text": "Html theme for sphinx documentation"
                                               }
                        , "software_license" : {"choices": ['GNU General Public License v3', 'MIT license'
                                                           , 'BSD license', 'ISC license'
                                                           , 'Apache Software License 2.0', 'Not open source'],
                                                "text": "software license"
                                               }
                        }
    selected = {}
    for name, description in preferences_setup.items():
        if name in options.overwrite_preferences:
            selected[name] = options.overwrite_preferences[name]
        else:
            try:
                selected[name] = et_micc2.config.get_param(name, description)
            except KeyboardInterrupt:
                print('Interupted - Preferences are not saved.')
                ctx.exit(1)

    # set some preferences for which the default is almost always ok
    selected['version'] = '0.0.0'  # default initial version number of a new projec
    selected["github_repo"] = "{{cookiecutter.project_name}}"  # default github repo name for a project
    selected["git_default_branch"] = "main"  # default git branch
    selected["minimal_python_version"] = "3.7"  # default minimal Python version"
    selected["py"] = "py"

    # Transfer the selected preferences to a Config object and save it to disk. 
    options.preferences = et_micc2.config.Config(**selected)
    save_to = __cfg_dir__ / __cfg_filename__
    print(f'These preferences are saved to {save_to}:\n{options.preferences}')
    answer = input("Continue? yes/no")
    if not answer.lower().startswith('n'):
        options.preferences.save(save_to, mkdir=True)
        print(f'Preferences saved to {save_to}.')
        ctx.exit(0)
    else:
        print('Interrupted. Preferences not saved.')
        ctx.exit(1)


####################################################################################################
# create
####################################################################################################
@main.command()
@click.option('--publish'
    , help="If specified, verifies that the package name is available on PyPI.\n"
           "If the result is False or inconclusive the project is NOT created."
    , default=False, is_flag=True
)
@click.option('-p', '--package'
    , help="Create a Python project with a package structure rather than a module structure:\n\n"
           "* package structure = ``<module_name>/__init__.py``\n"
           "* module  structure = ``<module_name>.py`` \n"
    , default=False, is_flag=True
)
@click.option('-d', '--description'
    , help="Short description of your project."
    , default='<Enter a one-sentence description of this project here.>'
)
@click.option('-T', '--template', help=__template_help, default=[])
@click.option('-n', '--allow-nesting'
    , help="If specified allows to nest a project inside another project."
    , default=False, is_flag=True
)
@click.option('--module-name'
    , help="use this name for the module, rather than deriving it from the project name."
    , default=''
)
@click.option('--remote'
    , help="Create remote repo on github. 'public'*|'private'|'none'"
    , default='public'
)
@click.argument('name', type=str, default='')
@click.pass_context
def create(ctx
           , name
           , package
           , module_name
           , description
           , template
           , allow_nesting
           , publish
           , remote
           ):
    """Create a new project skeleton.

    The project name is taken to be the last directory of the *project_path*.
    If this directory does not yet exist, it is created. If it does exist already, it
    must be empty.

    The package name is the derived from the project name, taking the
    `PEP8 module naming rules <https://www.python.org/dev/peps/pep-0008/#package-and-module-names>`_
    into account:

    * all lowercase.
    * dashes ``'-'`` and spaces ``' '`` replaced with underscores ``'_'``.
    * in case the project name has a leading number, an underscore is prepended ``'_'``.

    If *project_path* is a subdirectory of a micc project, *micc* refuses to continu,
    unless ``--allow-nesting`` is soecified.
    """
    options = ctx.obj

    if name:
        if not options.default_project_path:
            # global option -p and argument name were both specified.
            print( "ERROR: you specified both global option -p and argument 'name':"
                  f"         -p -> {options.project_path}"
                  f"         name -> {name}"
                   "       You must choose one or the other, not both."
                 )
            ctx.exit(-1)
        else:
            # overwrite the -p global option so the project will be created:
            options.project_path = Path(name).resolve()
            options.default_project_path = False

    options.package_structure = package
    options.publish = publish
    options.module_name = module_name
    if not remote in ['public','private', 'none']:
        print(f"ERROR: --remote={remote} is not recognized. Valid options are:\n"
              f"       --remote=public\n"
              f"       --remote=private\n"
              f"       --remote=none\n"
              )
        ctx.exit(-1)

    options.remote = None if remote=='none' else remote

    if not template:  # default is empty list
        if options.package_structure:
            template = [ 'package-base'
                       , 'package-general'
                       , 'package-simple-docs'
                       , 'package-general-docs'
                       ]
        else: # module structure
            template = [ 'package-base'
                       , 'package-simple'
                       , 'package-simple-docs'
                       ]
        options.templates = template

    options.allow_nesting = allow_nesting

    options.preferences.update(options.overwrite_preferences)

    options.template_parameters = {'project_short_description': underscore2space(description)}

    try:
        project = Project(options)
        project.create_cmd()
    except RuntimeError:
        ctx.exit(project.exit_code)


####################################################################################################
# convert_to_package
####################################################################################################
@main.command()
@click.option('--overwrite', is_flag=True
    , help="Overwrite pre-existing files (without backup)."
    , default=False
)
@click.option('--backup', is_flag=True
    , help="Make backup files (.bak) before overwriting any pre-existing files."
    , default=False
)
@click.pass_context
def convert_to_package(ctx, overwrite, backup):
    """Convert a Python module project to a package.

    A Python *module* project has only a ``<package_name>.py`` file, whereas
    a Python *package* project has ``<package_name>/__init__.py`` and can contain
    submodules, such as Python modules, packages and applications, as well as
    binary extension modules.

    This command also expands the ``package-general-docs`` template in this
    project, which adds a ``AUTHORS.rst``, ``HISTORY.rst`` and ``installation.rst``
    to the documentation structure.
    """
    options = ctx.obj
    options.overwrite = overwrite
    options.backup = backup
    
    try:
        project = Project(options)
        with et_micc2.logger.logtime(options):
            project.module_to_package_cmd()
    except RuntimeError:
        if project.exit_code == et_micc2.expand.EXIT_OVERWRITE:
            options.logger.warning(
                f"It is normally ok to overwrite 'index.rst' as you are not supposed\n"
                f"to edit the '.rst' files in '{options.project_path}{os.sep}docs.'\n"
                f"If in doubt: rerun the command with the '--backup' flag,\n"
                f"  otherwise: rerun the command with the '--overwrite' flag,\n"
            )
        ctx.exit(project.exit_code)

####################################################################################################
# info
####################################################################################################
@main.command()
@click.option('--name', is_flag=True
    , help="print the project name."
    , default=False
)
@click.option('--version', is_flag=True
    , help="print the project version."
    , default=False
)
@click.pass_context
def info(ctx,name,version):
    """Show project info.

    * file location
    * name
    * version number
    * structure (with ``-v``)
    * contents (with ``-vv``)

    Use verbosity to produce more detailed info.
    """
    options = ctx.obj

    try:
        project = Project(options)
    except RuntimeError:
        ctx.exit(project.exit_code)

    if name:
        print(project.package_name)
        return
    if version:
        print(project.version)
        return
    else:
        with et_micc2.logger.logtime(project):
            try:
                project.info_cmd()
            except RuntimeError:
                ctx.exit(project.exit_code)


####################################################################################################
# version
####################################################################################################
@main.command()
@click.option('-M', '--major'
    , help='Increment the major version number component and set minor and patch components to 0.'
    , default=False, is_flag=True
)
@click.option('-m', '--minor'
    , help='Increment the minor version number component and set minor and patch component to 0.'
    , default=False, is_flag=True
)
@click.option('-p', '--patch'
    , help='Increment the patch version number component.'
    , default=False, is_flag=True
)
@click.option('-r', '--rule'
    , help='Any semver 2.0 version string.'
    , default=''
)
@click.option('-t', '--tag'
    , help='Create a git tag for the new version, and push it to the remote repo.'
    , default=False, is_flag=True
)
@click.option('-s', '--short'
    , help='Print the version on stdout.'
    , default=False, is_flag=True
)
@click.option('-d', '--dry-run'
    , help='bumpversion --dry-run.'
    , default=False, is_flag=True
)
@click.pass_context
def version(ctx, major, minor, patch, rule, tag, short, dry_run):
    """Modify or show the project's version number."""
    options = ctx.obj

    if rule and (major or minor or patch):
        msg = ("Both --rule and --major|--minor|--patc specified.")
        click.secho("[ERROR]\n" + msg, fg='bright_red')
        ctx.exit(1)
    elif major:
        rule = 'major'
    elif minor:
        rule = 'minor'
    elif patch:
        rule = 'patch'

    options.rule = rule
    options.short = short
    options.dry_run = dry_run

    try:
        project = Project(options)
    except RuntimeError:
        ctx.exit(project.exit_code)

    with et_micc2.logger.logtime(project):
        try:
            project.version_cmd()
        except RuntimeError:    
            ctx.exit(project.exit_code)
        else:
            if tag:
                project.tag_cmd()


####################################################################################################
# tag
####################################################################################################
@main.command()
@click.pass_context
def tag(ctx):
    """Create a git tag for the current version and push it to the remote repo."""
    options = ctx.obj

    try:
        project = Project(options)
        project.tag_cmd()
    except RuntimeError:
        ctx.exit(project.exit_code)


####################################################################################################
# add
####################################################################################################
@main.command()
@click.option('--app'
    , default=False, is_flag=True
    , help="Add a CLI ."
)
@click.option('--group'
    , default=False, is_flag=True
    , help="Add a CLI with a group of sub-commands rather than a single command CLI."
)
@click.option('--py'
    , default=False, is_flag=True
    , help="Add a Python module."
)
@click.option('--package'
    , help="Add a Python module with a package structure rather than a module structure:\n\n"
           "* module  structure = ``<module_name>.py`` \n"
           "* package structure = ``<module_name>/__init__.py``\n\n"
           "Default = module structure."
    , default=False, is_flag=True
)
@click.option('--f90'
    , default=False, is_flag=True
    , help="Add a f90 binary extionsion module (Fortran)."
)
@click.option('--cpp'
    , default=False, is_flag=True
    , help="Add a cpp binary extionsion module (C++)."
)
@click.option('-T', '--templates', default='', help=__template_help)
@click.option('--overwrite', is_flag=True
    , help="Overwrite pre-existing files (without backup)."
    , default=False
)
@click.option('--backup', is_flag=True
    , help="Make backup files (.bak) before overwriting any pre-existing files."
    , default=False
)
@click.argument('name', type=str)
@click.pass_context
def add(ctx
        , name
        , app, group
        , py, package
        , f90
        , cpp
        , templates
        , overwrite
        , backup
        ):
    """Add a module or CLI to the projcect.

    :param str name: name of the CLI or module added.

    If ``app==True``: (add CLI application)

    * :py:obj:`app_name` is also the name of the executable when the package is installed.
    * The source code of the app resides in :file:`<project_name>/<package_name>/cli_<name>.py`.


    If ``py==True``: (add Python module)

    * Python source  in :file:`<name>.py*`or :file:`<name>/__init__.py`, depending on the :py:obj:`package` flag.

    If ``f90==True``: (add f90 module)

    * Fortran source in :file:`f90_<name>/<name>.f90` for f90 binary extension modules.

    If ``cpp==True``: (add cpp module)

    * C++ source     in :file:`cpp_<name>/<name>.cpp` for cpp binary extension modules.
    """
    options = ctx.obj
    options.add_name = name
    options.app = app
    options.group = group
    options.py = py
    options.package = package
    options.f90 = f90
    options.cpp = cpp
    options.templates = templates
    options.overwrite = overwrite
    options.backup = backup
    options.template_parameters = options.preferences.data
    try:
        project = Project(options)
        with et_micc2.logger.logtime(project):
            project.add_cmd()
    except RuntimeError:
        ctx.exit(project.exit_code)


####################################################################################################
# mv
####################################################################################################
@main.command()
@click.option('--silent', is_flag=True
    , help="Do not ask for confirmation on deleting a component."
    , default=False
)
@click.option('--entire-package', is_flag=True
    , help="Replace all occurences of <cur_name> in the entire package and in the ``tests`` directory."
    , default=False
)
@click.option('--entire-project', is_flag=True
    , help="Replace all occurences of <cur_name> in the entire project."
    , default=False
)
@click.argument('cur_name', type=str)
@click.argument('new_name', type=str, default='')
@click.pass_context
def mv(ctx, cur_name, new_name, silent, entire_package, entire_project):
    """Rename or remove a component, i.e an app (CLI) or a submodule.

    :param cur_name: name of component to be removed or renamed.
    :param new_name: new name of the component. If empty, the component will be removed.
    """
    options = ctx.obj

    options.cur_name = cur_name
    options.new_name = new_name
    options.silent = silent
    if new_name:
        options.entire_package, options.entire_project =  entire_package, entire_project
    # else these flags are ignored.

    try:
        project = Project(options)
        with et_micc2.logger.logtime(options):
            project.mv_component()
    except RuntimeError:
        ctx.exit(project.exit_code)


####################################################################################################
# build
####################################################################################################
@main.command()
@click.option('-m', '--module'
    , help="Build only this module. The module kind prefix (``cpp_`` "
           "for C++ modules, ``f90_`` for Fortran modules) may be omitted."
    , default=''
)
@click.option('-b', '--build-type'
    , help="build type: any of the standard CMake build types: "
           "DEBUG, MINSIZEREL, RELEASE, RELWITHDEBINFO."
    , default='RELEASE'
)
@click.option('--clean'
    , help="Perform a clean build."
    , default=False, is_flag=True
)
@click.option('--cleanup'
    , help="Cleanup build directory after successful build."
    , default=False, is_flag=True
)
@click.pass_context
def build( ctx
         , module
         , build_type
         , clean
         , cleanup
         ):
    """Build binary extensions."""
    options = ctx.obj
    options.build_options = SimpleNamespace( module_to_build = module
                                           , clean           = clean
                                           , cleanup         = cleanup
                                           , cmake           = {'CMAKE_BUILD_TYPE': build_type}
                                           )
    try:
        project = Project(options)
        with et_micc2.logger.logtime(options):
            project.build_cmd()
    except RuntimeError:
        ctx.exit(project.exit_code)


####################################################################################################
# check
####################################################################################################
@main.command()
# @click.option('--force', '-f', is_flag=True
#     , help="Overwrite existing setup."
#     , default=False
# )
@click.pass_context
def check( ctx
         ):
    """Check wether the current environment has all the neccessary tools available.

    Python packages:

    * Numpy
    * Pybind11
    * sphinx
    * sphinx-rtd-theme
    * sphinx-click

    Tools:

    * CMake
    * make
    * poetry
    * git
    * gh
    * compilers
    """
    if '3.8' < sys.version:
        check_cmd(ctx.obj)
    else:
        print("`micc2 check` requires python 3.8 or later.")


####################################################################################################
# doc
####################################################################################################
@main.command()
@click.pass_context
@click.argument('what', type=str, default='html')
def doc(ctx, what):
    """Build documentation."""
    options = ctx.obj
    options.what = what  
    try:
        project = Project(options)
        with et_micc2.logger.logtime(options):
            project.doc_cmd()
    except RuntimeError:
        ctx.exit(project.exit_code)



if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

# eof
