#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for et_micc2 package.
"""
#===============================================================================

import sys
from pathlib import Path
import subprocess

import pytest
from click.testing import CliRunner
from tests import helpers
#===============================================================================

import et_micc2.logger
from et_micc2 import cli_micc

#===============================================================================
# test scenario blocks
#===============================================================================
def micc2(arguments, stdin=None):
    """
    create a project 
    """
    runner = CliRunner()
    result = runner.invoke( cli_micc.main
                          , arguments
                          , input=stdin
                          )
    return helpers.report(result)


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

        with et_micc2.utils.in_directory('Foo'):
            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0


def test_scenario_package_structure():
    """
    """
    helpers.clear_test_workspace()
    with et_micc2.utils.in_directory(helpers.test_workspace):
        results = []
        result = micc2(['-vv', '-p', 'FOO', 'create', '--allow-nesting', '--remote=none', '--package'])
        assert Path('FOO/foo/__init__.py').exists()
        results.append(result)

        result = micc2(['-vvv', '-p', 'FOO', 'info'])
        results.append(result)

        with et_micc2.utils.in_directory('Foo'):
            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0

            result = micc2(['-v', 'add', 'added_py','--py'] )
            helpers.report(result)

            completed_process = subprocess.run(['pytest', 'tests'])
            assert completed_process.returncode == 0


if __name__ == "__main__":
    print(sys.version_info)
    the_test_you_want_to_debug = test_scenario_package_structure

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
        
 
# def test_scenario_1b():
#     """
#     """
#     runner = CliRunner()
# #     with runner.isolated_filesystem():
#     with in_empty_tmp_dir():
#         oops = Path('oops')
#         oops.touch()
#         with pytest.raises(AssertionError):
#             run(['-vv', 'create', '--allow-nesting'] )
#         l = os.listdir()
#         assert len(l)==1
#         
#         
# def test_scenario_2():
#     """
#     """
#     runner = CliRunner()
# #     with runner.isolated_filesystem():
#     with in_empty_tmp_dir():
#         run(['-p','foo','-vv', 'create', '--allow-nesting'])
#         foo = Path('foo')
#         et_micc2.utils.is_project_directory(foo,raise_if=False)
#         et_micc2.utils.is_module_project   (foo,raise_if=False)
#         et_micc2.utils.is_package_project  (foo,raise_if=True)
#         expected = '0.0.0'
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo.py')==expected
#         
#         run(['-p','foo','-vv', 'convert-to-package','--overwrite'])
#         et_micc2.utils.is_module_project   (foo,raise_if=True)
#         et_micc2.utils.is_package_project  (foo,raise_if=False)
# 
#         run(['-vv','-p','foo','version'])
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo' / '__init__.py')==expected
# 
#         run(['-p','foo','version', 'patch'])
#         expected = '0.0.1'
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo' / '__init__.py')==expected
#         
#         run(['-p','foo','version', 'minor'])
#         expected = '0.1.0'
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo' / '__init__.py')==expected
# 
#         run(['-p','foo','version', 'major'])
#         expected = '1.0.0'
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo' / '__init__.py')==expected
# 
#         run(['-p','foo','version', 'major'])
#         expected = '2.0.0'
#         assert get_version(foo / 'pyproject.toml')==expected
#         assert get_version(foo / 'foo' / '__init__.py')==expected
#         
#         result = run(['-p','foo','version', '-s'])
#         assert expected in result.stdout
#         
#         run(['-p','foo','-vv', 'add', '--app', 'my_app'])
#         assert Path('foo/foo/cli_my_app.py').exists()
#         
#         run(['-p','foo','-vv', 'add', 'mod1', '--py'])
#         assert Path('foo/foo/mod1.py').exists()
#         
#         run(['-p','foo','-vv', 'add', 'mod2', '--py', '--package'])
#         assert Path('foo/foo/mod2/__init__.py').exists()
# 
#         run(['-p','foo','-vv', 'add', 'mod3', '--f2py'])
#         assert Path('foo/foo/f2py_mod3/mod3.f90').exists()
#         print("f2py ok")
# 
#         run(['-p','foo','-vv', 'add', 'mod4', '--cpp'])
#         assert Path('foo/foo/cpp_mod4/mod4.cpp').exists()
#         print("cpp ok")
#         
#         extension_suffix = et_micc2.utils.get_extension_suffix()
#         run(['-p','foo','build'])
#         assert Path('foo/foo/mod3'+extension_suffix).exists()
#         assert Path('foo/foo/mod4'+extension_suffix).exists()
#         
#         run(['-p','foo','docs','--html','-l'])
#         assert Path('foo/docs/_build/html/index.html').exists()
#         assert Path('foo/docs/_build/latex/foo.pdf').exists()
#         print('make docs ok')
#         
#         run(['-p','foo','-vv','info'])
# 
# 
# def _test_add_dependency():
#     """
#     the outcome of this depends on whether we are online or not
#     this is mainly for debugging
#     """
#     runner = CliRunner()
#     with in_empty_tmp_dir():
#         run(['-vv', '-p', 'FOO', 'create', '--allow-nesting'])
#         assert Path('FOO/foo.py').exists()
#         with et_micc2.utils.in_directory('FOO'):
#             et_micc2.commands.add_dependencies(['numpy'],SimpleNamespace(verbosity=0))


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
# def test_scenario_2():
#     """
#     """
#     runner = CliRunner()
#     with in_empty_tmp_dir():
#         run(['-vv', '-p', 'FOO', 'create', '-p', '--allow-nesting'])
#         assert Path('FOO/foo/__init__.py').exists()
#         run(['-vvv', '-p', 'FOO', 'info'])
#         run(['-v', '-p', 'FOO', 'version'])
#         run(['-v', '-p', 'FOO', 'version','--short'])
#         run(['-vv', '-p', 'FOO', 'version','-M'])
#         run(['-v', '-p', 'FOO', 'version','--short'])
#         run(['-vv', '-p', 'FOO', 'version','-m'])
#         run(['-v', '-p', 'FOO', 'version','--short'])
#         run(['-vv', '-p', 'FOO', 'version','-p'])
#         run(['-v', '-p', 'FOO', 'version','--short'])
# ==============================================================================
