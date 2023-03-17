#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for et_micc2 package.
"""
#===============================================================================
import importlib
import traceback
import os
from pathlib import Path
import pytest
import subprocess
import sys

from click.testing import CliRunner

sys.path.insert(0,'.')
sys.path.insert(0,'..')

from tests import helpers

# import et_micc2.tools.messages as messages
from et_micc2 import cli_micc
import et_micc2.tools.env as env
import et_micc2.tools.project as project
import et_micc2.tools.utils as utils
import et_micc2.subcmds.build as build

#===============================================================================
__skip_build_f90__ = subprocess.run('f2py').returncode != 0 # while f2py is failing

#===============================================================================
# test scenario blocks
#===============================================================================
def micc(arguments, stdin=None, assert_exit_code=True):
    """
    helper function to run cli_micc.py with arguments
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
            raise AssertionError(f"result.exit_code == {result.exit_code}")

    return result


#===============================================================================
#   Tests
#===============================================================================
def test_micc_help():
    """
    Test ``et_micc2 --help``.
    """
    result = micc(['--help'])
    assert '--help' in result.output
    assert 'Show this message and exit.' in result.output


def test_clear_test_workspace():
    """ 
    """
    helpers.clear_test_workspace()
    p = helpers.test_workspace
    assert p.exists()
    print(f"* assert {str(helpers.test_workspace)}.exists()=={p.exists()}")
    
    pFOO = p / 'FOO'
    pFOO.mkdir()
    assert pFOO.exists()
    helpers.clear_test_workspace()
    assert not pFOO.exists()
    assert p.exists()
    print('* helpers.clear_test_workspace() works on empty subfolder')

    pFOO.mkdir()
    pbar = pFOO / 'bar.txt'
    with pbar.open('w') as f:
        f.write("some text\n")
    assert pbar.exists()
    helpers.clear_test_workspace()
    assert not pbar.exists()
    assert not pFOO.exists()
    assert p.exists()
    print('* helpers.clear_test_workspace() works on non-empty subfolder')

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
    print('* helpers.clear_test_workspace("FOO") selectively removes subfolder "FOO."')

def obsolete_test_scenario_module_structure():
    # this test is obsolete since we decided that the top level package is always a module/__init__.py
    helpers.clear_test_workspace()
    with utils.in_directory(helpers.test_workspace):
        results = []
        result = micc(['-vv', '-p', 'FOO', 'create', '--allow-nesting', '--remote=none'])
        assert Path('FOO/foo.py').exists()
        results.append(result)

        result = micc(['-vvv', '-p', 'FOO', 'info'])
        results.append(result)

        with utils.in_directory('FOO'):
            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0

            if 'VSC_HOME' in os.environ:
                print('Not testing build documentation')
            else:
                # test building documentation
                with utils.in_directory('docs'):
                    completed_process = subprocess.run(['make', 'html'])
                    assert completed_process.returncode == 0

            result = micc(['version'])
            assert 'Project (FOO) version (0.0.0)' in result.output
            result = micc(['version', '-p'])
            assert '(FOO)> version (0.0.0) -> (0.0.1)' in result.output
            result = micc(['version', '-p'])
            assert '(FOO)> version (0.0.1) -> (0.0.2)' in result.output
            result = micc(['version', '-m'])
            assert '(FOO)> version (0.0.2) -> (0.1.0)' in result.output
            result = micc(['version', '-m'])
            assert '(FOO)> version (0.1.0) -> (0.2.0)' in result.output
            result = micc(['version', '-p'])
            assert '(FOO)> version (0.2.0) -> (0.2.1)' in result.output
            result = micc(['version', '-M'])
            assert '(FOO)> version (0.2.1) -> (1.0.0)' in result.output
            result = micc(['version', '-s'])
            assert '1.0.0' in result.output
    # helpers.clear_test_workspace()


def test_package():
    helpers.clear_test_workspace()

    with utils.in_directory(helpers.test_workspace):
        results = []
        #Create package BAR
        result = micc(['-vv', '-p', 'BAR', 'create', '--allow-nesting', '--remote=none'])
        assert Path('BAR/bar/__init__.py').exists()
        results.append(result)

        result = micc(['-vvv', '-p', 'BAR', 'info'])
        results.append(result)

        with utils.in_directory('BAR'):
            completed_process = subprocess.run(['pytest', 'tests/bar'])
            assert completed_process.returncode == 0
            # Add a python sub-module
            submodule = 'submodule_py'
            result = micc(['-v', 'add', submodule, '--py'] )

            completed_process = subprocess.run(['pytest', 'tests/bar/'])
            assert completed_process.returncode == 0

            # Add a binary sub-module
            for flag in ['--cpp','--f90']:
                submodule = f'submodule_{flag[2:]}'
                result = micc(['-v', 'add', submodule, flag])
                # test micc build
                if flag == '--f90' and __skip_build_f90__:
                    print('skipping build f90 because f2py is missing.')
                    continue
                # We are relying on automatic build here. This also tests the `micc build` command
                completed_process = subprocess.run(['pytest', 'tests/bar/'])

                extension_suffix = build.get_extension_suffix()
                binary_extension = Path(f'bar/{submodule}{extension_suffix}')
                assert binary_extension.exists()

            for cli, cli_flag in zip(['clibar','clibarsup'], ['--cli','--clisub']):
                result = micc(['-v', 'add', cli, cli_flag])
                completed_process = subprocess.run(['pytest', 'tests/bar/'])
                assert completed_process.returncode == 0

            if 'VSC_HOME' in os.environ:
                print('Not testing build documentation')
            else:
                # test building documentation
                with utils.in_directory('docs'):
                    completed_process = subprocess.run(['make', 'html'])
                    assert completed_process.returncode == 0
    


def test_git_missing():
    """"""
    helpers.clear_test_workspace()

    env.ToolInfo.mock = ['git']

    with utils.in_directory(helpers.test_workspace):
        #Create package NOGIT
        result = micc( ['-vv', '--silent', 'create', 'NOGIT', '--allow-nesting', '--remote=none']
                     , assert_exit_code=False
                     )
        assert result.exit_code == env.ExitCodes.MISSING_COMPONENT.value
        assert not Path('NOGIT/nogit/__init__.py').exists()

    env.ToolInfo.mock = []


def test_gh_missing():
    """"""
    helpers.clear_test_workspace()
    
    env.ToolInfo.mock = ['gh']

    with utils.in_directory(helpers.test_workspace):
        results = []
        #Create package NOGH
        result = micc( ['-vv', '--silent', 'create', 'NOGH', '--allow-nesting']
                     , assert_exit_code=False
                     )
        assert result.exit_code == env.ExitCodes.MISSING_COMPONENT.value
        assert not Path('NOGH/nogh/__init__.py').exists()
        results.append(result)

    env.ToolInfo.mock = []


def test_cmake_missing():
    """"""
    helpers.clear_test_workspace()

    env.ToolInfo.mock = ['cmake']

    with utils.in_directory(helpers.test_workspace):
        #Create package NOCMAKE
        result = micc( ['-vv', '--silent', 'create', 'NOCMAKE', '--remote=none', '--allow-nesting']
                      , assert_exit_code=False
                      )
        assert result.exit_code == 0
        assert Path('NOCMAKE/nocmake/__init__.py').exists()

        with utils.in_directory('NOCMAKE'):
            # Add a binary sub-module
            for flag in ['--cpp', '--f90']:
                submodule = f'submodule_{flag[2:]}'
                result = micc(['-v', 'add', submodule, flag], assert_exit_code=False)
                assert result.exit_code == 0

            result = micc(['-v', 'build', 'submodule_cpp'], assert_exit_code=False)
            assert result.exit_code == env.ExitCodes.MISSING_COMPONENT.value

    env.ToolInfo.mock = []

def test_f2py_missing():
    """"""
    helpers.clear_test_workspace()

    env.ToolInfo.mock = ['f2py']

    with utils.in_directory(helpers.test_workspace):
        #Create package nof2py
        result = micc( ['-vv', '--silent', 'create', 'nof2py', '--remote=none', '--allow-nesting']
                     , assert_exit_code=False
                     )
        assert result.exit_code == 0
        assert Path('nof2py/nof2py/__init__.py').exists()

        with utils.in_directory('nof2py'):
            # Add a binary sub-module
            for flag in ['--f90']:
                submodule = f'submodule_{flag[2:]}'
                result = micc(['-v', 'add', submodule, flag], assert_exit_code=False)
                assert result.exit_code == 0
                result = micc(['-v', 'build', submodule], assert_exit_code=False)
                assert result.exit_code == env.ExitCodes.MISSING_COMPONENT.value

    env.ToolInfo.mock = []


def test_pybind11_missing():
    """"""
    helpers.clear_test_workspace()

    env.PkgInfo.mock = ['pybind11']

    with utils.in_directory(helpers.test_workspace):
        #Create package nopybind11
        result = micc( ['-vv', '-p', 'nopybind11', 'create', '--remote=none', '--allow-nesting']
                      , assert_exit_code=False
                      )
        assert result.exit_code == 0
        assert Path('nopybind11/nopybind11/__init__.py').exists()

        with utils.in_directory('nopybind11'):
            # Add a binary sub-module
            for flag in ['--cpp']:
                submodule = f'submodule_{flag[2:]}'
                result = micc(['-v', 'add', submodule, flag], assert_exit_code=False)
                assert result.exit_code == 0
                # test micc build
                result = micc(['-vv', 'build', submodule], assert_exit_code=False)
                assert result.exit_code == env.ExitCodes.MISSING_COMPONENT.value

    env.PkgInfo.mock = []


def test_doc_cmd():
    helpers.clear_test_workspace()
    if 'VSC_HOME' in os.environ:
        print('Not testing build documentation')
    else:
        with utils.in_directory(helpers.test_workspace):
            #Create package nopybind11
            result = micc( ['-vv', '-p', 'DOC', 'create', '--remote=none', '--allow-nesting']
                          , assert_exit_code=False
                          )
            assert result.exit_code == 0
            assert Path('DOC/docs').exists()
            result = micc( ['-vv', '-p', 'DOC', 'doc'])
            assert (Path('DOC/docs') / '_build/html/index.html').exists()


if __name__ == "__main__":
    print(sys.version_info)
    the_test_you_want_to_debug = test_pybind11_missing

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
