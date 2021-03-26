# -*- coding: utf-8 -*-
"""
Module et_micc2.check_environment
=================================

This submodule implements the ``micc check`` command.

It checks the environment for Python packages and tools micc2 depends on.
"""

import os
import subprocess
import importlib
from importlib.metadata import version

def check_tool(tool,local):
    completed_which = subprocess.run(['which', tool], capture_output=True, text=True)
    if completed_which.returncode !=0:
        print(f'    {tool} is not available.')
        return False
    else:
        completed_version = subprocess.run([tool, '--version'], capture_output=True, text=True)
        version_string = completed_version.stdout.strip().replace('\n',' ')
        if local:
            print(f'    {tool} is available: {version_string}')
            return True
        else: # VSC cluster
            if not completed_which.output.startswith('/Apps/'):
                which_string = completed_which.stdout.strip().replace('\n', ' ')
                print( '   {tool} is available from the system:\n'
                      f'       {which_string}'
                      f'       {version_string}'
                       '   However, it is recommended to use a cluster module version.')
                return False
            else:
                print(f'    {tool} is available; {completed_version.stdout.strip()}')
                return True

def check_cmd(options):
    """
    """
    
    where = os.environ['VSC_INSTITUTE_CLUSTER'] if getattr(os.environ, 'VSC_HOME', '') else 'local'
    local = where=='local'

    if not local:
        # check that we are not using the system Python:
        completed_which = subprocess.run(['which', 'python'])
        if not '/Apps/' in completed_which.output:
            click.secho('The system python ({completed_which.output.strip()}) is not suitable for development.\n'
                        'use `module load` to load a appropriate Python distribution.', fg='bright_red')

    # format strings
    pip_install         = '    To install it, run `pip install {module_name}` in your environment.'
    pip_install_cluster = '    To install it, run `PYTHONUSERBASE=$VSC_DATA/.local/ python -m pip install --user {module_name}`'
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
    print('Checking Python packages:')
    for module_name, version_needed in modules.items():
        try:
            m = importlib.import_module(module_name)
            version = importlib.metadata.version(module_name)
            if version < version_needed:
                click.secho(f'{module_name}: FOUND {version}, but expecting {version_needed}', fg='bright_red')
            else:
                print(f'{module_name}: {version} is OK (>={version_needed}).')
                if options.verbosity > 1:
                    print(f'    {m}')
        except ModuleNotFoundError:
            click.secho(f'{m}: NOT FOUND, need {modules[module_name]}', fg='bright_red')
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
                    print('    You must use your local machine for building documentation.\n'
                          '    The cluster is not suited for this.')
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

    print('\nChecking tools:')
    # git
    print('- VCS:')
    if check_tool('git', local):
        can_git = True
    if check_tool('gh', local):
        can_gh = True

    # CMake
    print('- CMake:')
    if not check_tool('cmake', local):
        can_build_f90 = False
        can_build_cpp = False

    # compilers
    print('- Compilers:')
    check_tool('g++', local)
    check_tool('icpc', local)
    check_tool('gcc', local)
    check_tool('gfortran', local)
    check_tool('ifort', local)

    print('\nYour environment is ready to:')
    print('  - use poetry (e.g. `poetry publish --build`:', 'YES' if can_poetry    else 'NO')
    print('  - use pytest for automating tests          :', 'YES' if can_pytest    else 'NO')
    print('  - build binary extension from C++          :', 'if C++ compiler available' if can_build_cpp else 'NO')
    print('  - build binary extension from Fortran      :', 'if Fortran and C compiler available' if can_build_f90 else 'NO')
    print('  - build command line interfaces with click :', 'YES' if can_build_cli else 'NO')
    print('  - generate documentation with sphinx       :', 'YES' if can_build_doc else 'NO')
    print('  - git                                      :', 'YES' if can_git else 'NO')
    print('  - create remote repositories at github.com :', 'YES' if can_gh else 'NO')
