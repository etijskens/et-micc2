#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for et_micc2 package.
"""
#===============================================================================

import sys,os
from pathlib import Path
import subprocess
import importlib

import pytest
from click.testing import CliRunner
from tests import helpers
#===============================================================================

import et_micc2.logger
from et_micc2 import cli_micc

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


def test_scenario_package_structure():
    """
    """
    helpers.clear_test_workspace()
    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        #Create package FOO
        result = micc2(['-vv', '-p', 'FOO', 'create', '--allow-nesting', '--remote=none', '--package'])
        assert Path('FOO/foo/__init__.py').exists()
        results.append(result)

        result = micc2(['-vvv', '-p', 'FOO', 'info'])
        results.append(result)

        with et_micc2.utils.in_directory('FOO'):
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
                binary_extension = Path(f'foo/{submodule}{extension_suffix}')
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

            # test building documentation
            with et_micc2.utils.in_directory('docs'):
                completed_process = subprocess.run(['make', 'html'])
                assert completed_process.returncode == 0

if __name__ == "__main__":
    print(sys.version_info)
    the_test_you_want_to_debug = test_scenario_module_structure

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
