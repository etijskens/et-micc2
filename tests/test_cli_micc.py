#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for et_micc2 package.
"""
#===============================================================================
import sys
sys.path.insert(0,'.')
sys.path.insert(0,'..')
import traceback
import os
from pathlib import Path
import subprocess
import importlib

import pytest
from click.testing import CliRunner
from tests import helpers
#===============================================================================

import et_micc2.logger
from et_micc2 import cli_micc, project


#===============================================================================
# test scenario blocks
#===============================================================================
def micc2(arguments, stdin=None, assert_exit_code=True):
    """
    create a project 
    """
    runner = CliRunner()
    result = runner.invoke( cli_micc.main, arguments, input=stdin)
    
    print(result.output)

    if result.exception:
        if result.stderr_bytes:
            print(result.stderr)
        print('exit_code =', result.exit_code)
        print(result.exception)
        traceback.print_tb(result.exc_info[2])
        print(result.exc_info[2])

    if assert_exit_code:
        if result.exit_code:
            raise AssertionError(f"result.exit_code = {result.exit_code}")

    return result


#===============================================================================
#   Tests
#===============================================================================
def test_micc_help():
    """
    Test ``et_micc2 --help``.
    """
    result = micc2(['--help'])
    assert '--help' in result.output
    assert 'Show this message and exit.' in result.output


def test_clear_test_workspace():
    """ 
    """
    helpers.clear_test_workspace()
    p = Path('test_workspace')
    assert p.exists()
    print(1)
    
    pFOO = p / 'FOO'
    pFOO.mkdir()
    assert pFOO.exists()
    helpers.clear_test_workspace()
    assert not pFOO.exists()
    assert p.exists()
    print(2)

    pFOO.mkdir()
    pbar = pFOO / 'bar.txt'
    with pbar.open('w') as f:
        f.write("some text\n")
    assert pbar.exists()
    helpers.clear_test_workspace()
    assert not pbar.exists()
    assert not pFOO.exists()
    assert p.exists()
    print(3)

    pFOO.mkdir()
    pKeep = p / 'Keep'
    pKeep.mkdir()
    assert pKeep.exists()
    with pbar.open('w') as f:
        f.write("some text\n")
    assert pbar.exists()
    helpers.clear_test_workspace('FOO')
    assert not pbar.exists()
    assert not pFOO.exists()
    assert pKeep.exists()
    print(4)



def test_scenario_module_structure():
    """
    """
    helpers.clear_test_workspace()
    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        result = micc2(['-vv', '-p', 'FOO', 'create', '--allow-nesting', '--remote=none'])
        assert Path('FOO/foo.py').exists()
        results.append(result)

        result = micc2(['-vvv', '-p', 'FOO', 'info'])
        results.append(result)

        with et_micc2.utils.in_directory('FOO'):
            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0

            if 'VSC_HOME' in os.environ:
                print('Not testing build documentation')
            else:
                # test building documentation
                with et_micc2.utils.in_directory('docs'):
                    completed_process = subprocess.run(['make', 'html'])
                    assert completed_process.returncode == 0

            result = micc2(['version'])
            assert 'Project (FOO) version (0.0.0)' in result.output
            result = micc2(['version', '-p'])
            assert '(FOO)> version (0.0.0) -> (0.0.1)' in result.output
            result = micc2(['version', '-p'])
            assert '(FOO)> version (0.0.1) -> (0.0.2)' in result.output
            result = micc2(['version', '-m'])
            assert '(FOO)> version (0.0.2) -> (0.1.0)' in result.output
            result = micc2(['version', '-m'])
            assert '(FOO)> version (0.1.0) -> (0.2.0)' in result.output
            result = micc2(['version', '-p'])
            assert '(FOO)> version (0.2.0) -> (0.2.1)' in result.output
            result = micc2(['version', '-M'])
            assert '(FOO)> version (0.2.1) -> (1.0.0)' in result.output
            result = micc2(['version', '-s'])
            assert '1.0.0' in result.output
    # helpers.clear_test_workspace()


def test_scenario_package_structure():
    """
    """
    # helpers.clear_test_workspace()
    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        #Create package BAR
        result = micc2(['-vv', '-p', 'BAR', 'create', '--allow-nesting', '--remote=none', '--package'])
        assert Path('BAR/bar/__init__.py').exists()
        results.append(result)

        result = micc2(['-vvv', '-p', 'BAR', 'info'])
        results.append(result)

        with et_micc2.utils.in_directory('BAR'):
            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0

            # Add a python sub-module
            for submodule, flag in zip(['added_py','added_pyp'], ['--py','--package']):
                result = micc2(['-v', 'add', submodule, flag] )

                completed_process = subprocess.run(['pytest', f'tests/test_{submodule}.py'])
                assert completed_process.returncode == 0

            # Add a binary sub-module
            for flag in ['--cpp','--f90']:
                submodule = f'added_{flag[2:]}'
                result = micc2(['-v', 'add', submodule, flag])
                # test micc build
                result = micc2(['-vv', 'build', '-m', submodule, '--clean'] )
                extension_suffix = et_micc2.project.get_extension_suffix()
                binary_extension = Path(f'bar/{submodule}{extension_suffix}')
                assert binary_extension.exists()

                # test auto build:
                os.remove(binary_extension)
                assert not binary_extension.exists()

                completed_process = subprocess.run(['which', 'python'])
                # This is not the python from the micc2 .venv, but the one from pyenv.
                # I made this working by putting a symbolic link to the et_micc2 directory in the
                # site-packages folder of /Users/etijskens/.pyenv/versions/3.8.5/bin/python.
                # attempts to make it work with this python
                # python = str(helpers.test_workspace / '../.venv/bin/python')
                # fail because pybind11 is not found..'

                # completed_process = subprocess.run([python, '-c', 'import et_micc2'])
                # assert completed_process.returncode == 0
                completed_process = subprocess.run(['python', '-m', 'pytest', f'tests/test_{flag[2:]}_{submodule}.py'])
                assert completed_process.returncode == 0
                assert binary_extension.exists()

            for app, flag in zip(['app','app_with_subcommands'], ['--app','--group']):
                result = micc2(['-v', 'add', app, flag])

                completed_process = subprocess.run(['python', '-m', 'pytest', f'tests/test_cli_{app}.py'])
                assert completed_process.returncode == 0

            if 'VSC_HOME' in os.environ:
                print('Not testing build documentation')
            else:
                # test building documentation
                with et_micc2.utils.in_directory('docs'):
                    completed_process = subprocess.run(['make', 'html'])
                    assert completed_process.returncode == 0
    # helpers.clear_test_workspace()


def test_git_missing():
    """"""
    helpers.clear_test_workspace()

    project.ToolInfo.mock = ['git']

    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        #Create package NOGIT
        result = micc2( ['-vv', '-p', 'NOGIT', 'create', '--allow-nesting', '--remote=none', '--package']
                      , stdin='\n', assert_exit_code=False
                      )
        assert result.exit_code == -1
        assert not Path('NOGIT/nogit/__init__.py').exists()
        results.append(result)

    project.ToolInfo.mock = []


def test_gh_missing():
    """"""
    project.ToolInfo.mock = ['gh']

    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        #Create package NOGH
        result = micc2( ['-vv', '-p', 'NOGH', 'create', '--allow-nesting', '--package']
                      , stdin='\n', assert_exit_code=False
                      )
        assert result.exit_code == -1
        assert not Path('NOGH/nogh/__init__.py').exists()
        results.append(result)

    project.ToolInfo.mock = []


def test_cmake_missing():
    """"""
    helpers.clear_test_workspace()

    project.ToolInfo.mock = ['cmake']

    with et_micc2.utils.in_directory(helpers.test_workspace):
        #Create package NOCMAKE
        result = micc2( ['-vv', '-p', 'NOCMAKE', 'create', '--remote=none', '--allow-nesting', '--package']
                      , stdin='\n', assert_exit_code=False
                      )
        assert result.exit_code == 0
        assert Path('NOCMAKE/nocmake/__init__.py').exists()

        with et_micc2.utils.in_directory('NOCMAKE'):
            # Add a binary sub-module
            for flag in ['--cpp', '--f90']:
                submodule = f'added_{flag[2:]}'
                result = micc2(['-v', 'add', submodule, flag])
                assert result.exit_code == 0
                # # test micc build
                # result = micc2(['-vv', 'build', '-m', submodule, '--clean'])
                # extension_suffix = et_micc2.project.get_extension_suffix()
                # binary_extension = Path(f'bar/{submodule}{extension_suffix}')
                # assert binary_extension.exists()

    project.ToolInfo.mock = []

def test_pybind11_f2py_missing():
    """"""
    helpers.clear_test_workspace()

    project.ToolInfo.mock = ['f2py']
    project.ModuleInfo.mock = ['pybind11']

    with et_micc2.utils.in_directory(helpers.test_workspace):
        #Create package nopybind11_nof2py
        result = micc2( ['-vv', '-p', 'nopybind11_nof2py', 'create', '--remote=none', '--allow-nesting', '--package']
                      , stdin='\n', assert_exit_code=False
                      )
        assert result.exit_code == 0
        assert Path('nopybind11_nof2py/nopybind11_nof2py/__init__.py').exists()

        with et_micc2.utils.in_directory('nopybind11_nof2py'):
            # Add a binary sub-module
            for flag in ['--cpp', '--f90']:
                submodule = f'added_{flag[2:]}'
                result = micc2(['-v', 'add', submodule, flag])
                assert result.exit_code == 0
                # # test micc build
                # result = micc2(['-vv', 'build', '-m', submodule, '--clean'])
                # extension_suffix = et_micc2.project.get_extension_suffix()
                # binary_extension = Path(f'bar/{submodule}{extension_suffix}')
                # assert binary_extension.exists()

    project.ToolInfo.mock = []
    project.ModuleInfo.mock = []


def test_build_pybind11_missing():
    """"""
    helpers.clear_test_workspace()

    project.ModuleInfo.mock = ['pybind11']

    with et_micc2.utils.in_directory(helpers.test_workspace):
        #Create package nopybind11
        result = micc2( ['-vv', '-p', 'nopybind11', 'create', '--remote=none', '--allow-nesting', '--package']
                      , stdin='\n', assert_exit_code=False
                      )
        assert result.exit_code == 0
        assert Path('nopybind11/nopybind11/__init__.py').exists()

        with et_micc2.utils.in_directory('nopybind11'):
            # Add a binary sub-module
            for flag in ['--cpp']:
                submodule = f'added_{flag[2:]}'
                result = micc2(['-v', 'add', submodule, flag])
                assert result.exit_code == 0
                # test micc build
                result = micc2(['-vv', 'build', '-m', submodule, '--clean'], assert_exit_code=False)
                assert result.exit_code !=0

    project.ToolInfo.mock = []
    project.ModuleInfo.mock = []


if __name__ == "__main__":
    print(sys.version_info)
    the_test_you_want_to_debug = test_build_pybind11_missing

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
