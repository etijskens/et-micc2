# -*- coding: utf-8 -*-
"""
Module et_micc2.check_environment
=================================

This submodule implements the ``micc check`` command.

It checks the environment for Python packages and tools micc2 depends on.
"""

import os,sys
import subprocess
import importlib
from importlib.metadata import version
import click

def check_tool(tool,local,not_required_message=None):
    """
    :param str tool: name of executable, e.g. 'cmake'
    """
    completed_which = subprocess.run(['which', tool], capture_output=True, text=True)
    which_string = completed_which.stdout.strip().replace('\n', ' ')
    if completed_which.returncode !=0:
        click.secho(f'    {tool} is not available.', fg='bright_red')
        if not_required_message:
            print(f'      {not_required_message}') 
        return False
    else:
        completed_version = subprocess.run([tool, '--version'], capture_output=True, text=True)
        version_string = completed_version.stdout.strip().replace('\n\n','\n').replace('\n','\n        ')
        if local:
            click.secho(f'    {tool} is available:', fg='green')
            print(f'      {version_string}')
            print(f'      {which_string}')
            return True
        else: # VSC cluster
            
            if completed_which.stdout.startswith('/usr/bin/'):                
                click.secho(f'   {tool} is available from the system. However, it is recommended to use a cluster module version.'
                           , fg='bright_red'
                           )
                print(      f'     {which_string}\n'
                            f'     {version_string}\n')
                return False
            else:
                click.secho(f'    {tool} is available:', fg='green')
                print(f'      {version_string}')
                print(f'      {which_string}')
                return True


def check_cmd(options):
    """
    """
    
    where = os.environ['VSC_INSTITUTE_CLUSTER'] if 'VSC_HOME' in os.environ else 'local'
    local = where=='local'

    print('Python\n'
          '------')
    completed_which = subprocess.run(['which', 'python'],text=True,capture_output=True)
    which_string = completed_which.stdout.replace('\n', '')

    print(f'python = {which_string}')
    python_version = sys.version.replace('\n', ' ')
    print(f'version= {python_version}')
    if not local:
        # check that we are not using the system Python:
        if '/usr/bin/' in which_string:
            click.secho(f'The system python is not suitable for development.\n'
                         'use `module load` to load a appropriate Python distribution.', fg='bright_red')

    # format strings
    pip_install         = '    To install it, run `python -m pip install {module_name}` in your virtual environment, or\n'\
                          '    `pip install python -m pip install --user {module_name}`'
    pip_install_cluster = '    To install it, run `python -m pip install --user {module_name}`'
    load_module = '    Load a cluster module containing {module_name}.'

    can_build_doc = True
    can_build_cpp = True
    can_build_f90 = True
    can_build_cli = True
    can_pytest    = True
    can_poetry    = True
    can_git       = True
    can_gh        = True

    modules = {'numpy'              : '1.17.0'
              ,'pybind11'           : '2.6.2'
              ,'sphinx'             : '3.4'
              ,'sphinx_rtd_theme'   : '0.5'
              ,'sphinx_click'       : '2.7'
              ,'click'              : '7.0'
              ,'pytest'             : '5.0'
              }
    print('\nPython packages'
          '\n---------------')
    for module_name, version_needed in modules.items():
        try:
            m = importlib.import_module(module_name)
            version = importlib.metadata.version(module_name)
            if version < version_needed:
                click.secho(f'\n{module_name}: FOUND {version}, but expecting {version_needed}', fg='bright_red')
            else:
                print(f'\n{module_name}: {version} is OK (>={version_needed}).')
                if options.verbosity > 1:
                    print(f'    {m}')
        except ModuleNotFoundError:
            fg = 'bright_red'
            click.secho(f'\n{module_name}: NOT FOUND, need {modules[module_name]} or later', fg=fg)
            s = None
            if module_name=='numpy':
                print(f'    {module_name} is needed for building binary extensions from Fortran.')
                s = pip_install if local else load_module
                can_build_f90 = False

            elif module_name=='pybind11':
                print(f'    {module_name} is needed for building binary extensions from C++.')
                s = pip_install if local else pip_install_cluster
                can_build_cpp = False

            elif module_name.startswith('sphinx'):
                if local:
                    print(f'    Sphinx is only needed to build documentation.')
                    s = pip_install
                else:
                    print('    It is discouraged to build documentation on the cluster. Please consider building documentation on a desktop.')
                can_build_doc = False

            elif 'click' in module_name:
                print('    Click is only needed for building CLIs.')
                s = pip_install if local else pip_install_cluster
                can_build_cli = False

            elif module_name=='pytest':
                print(f'    {module_name} is needed for automating tests.')
                s = pip_install if local else '\n'.join([pip_install_cluster, load_module])
                can_pytest = False

            else:
                print(f'    No recommandation for missing {module_name}.')

            if s:
                print(s.format(module_name=module_name))

    print('\n'
          'Tools\n'
          '-----')
    # poetry
    print('\n- poetry:')
    not_required_message = 'The use of Poetry is discouraged on the cluster.' if not local else None
    can_poetry = check_tool('poetry', local, not_required_message=not_required_message)
        
    # git
    print('\n- VCS:')
    can_git = check_tool('git', local)
    can_gh = check_tool('gh', local)

    # CMake
    print('\n- CMake:')
    if not check_tool('cmake', local):
        can_build_f90 = False
        can_build_cpp = False

    # compilers
    print('\n- Compilers:')
    check_tool('g++', local)
    print()
    check_tool('icpc', local)
    print()
    check_tool('gcc', local)
    print()
    check_tool('gfortran', local)
    print()
    check_tool('ifort', local)

    print('\nYour environment is ready to:')
    print('  - use poetry (e.g. `poetry publish --build`):', 'YES' if can_poetry    else 'NO')
    print('  - use pytest for automating tests           :', 'YES' if can_pytest    else 'NO')
    print('  - build binary extensions from C++          :', 'if a C++ compiler is available' if can_build_cpp else 'NO')
    print('  - build binary extensions from Fortra       :', 'if a Fortran and a C compiler are available' if can_build_f90 else 'NO')
    print('  - build command line interfaces with click  :', 'YES' if can_build_cli else 'NO')
    print('  - generate documentation with sphinx        :', 'YES' if can_build_doc else 'NO')
    print('  - git                                       :', 'YES' if can_git       else 'NO')
    print('  - create remote repositories at github.com  :', 'YES' if can_gh        else 'NO')
