#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

import pytest

"""Tests for `micc` package."""
from pathlib import Path
from types import SimpleNamespace

import et_micc2.tools.env as env
import et_micc2.tools.project as project
import et_micc2.tools.utils as utils

from tests import helpers

def test_rename_remove_1():
    """test rename and remove of submodules and cli components"""
    with utils.in_directory(helpers.test_workspace()):
        component_flags = ['--py', '--f90', '--cpp', '--cli', '--clisub']
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').exists()
        # add component 'submod' for every different component flag
        for flag in component_flags:
            component_name = f"submod_{flag[2:]}"
            results.append(helpers.micc(['-p', 'BAR', 'add', component_name, flag]))
            if 'cli' in flag:
                assert (Path('.') / 'BAR' / 'bar/cli' / f"{component_name}.py").is_file()
            else:
                assert (Path('.') / 'BAR' / 'bar' / component_name).is_dir()

        # rename components submod -> foo
        for flag in component_flags:
            component_name  = f"submod_{flag[2:]}"
            component_new_name = f'foo_{flag[2:]}'
            results.append(helpers.micc(['-p', 'BAR', 'mv', component_name, component_new_name]))
            if 'cli' in flag:
                assert (Path('.') / 'BAR' / 'bar' / 'cli' / f"{component_new_name}.py").is_file()
                assert (Path('.') / 'BAR' / 'tests' / 'bar' / 'cli' / f"test_{component_new_name}.py").is_file()
            else:
                assert (Path('.') / 'BAR' / 'bar' / component_new_name).is_dir()
                assert (Path('.') / 'BAR' / 'tests' / 'bar' / component_new_name).is_dir()

        # remove foo
        for flag in component_flags:
            component_new_name = f'foo_{flag[2:]}'
            results.append(helpers.micc(['-p', 'BAR', 'mv', component_new_name]))
            if 'cli' in flag:
                assert not (Path('.') / 'BAR' / 'bar' / f"cli_{component_new_name}.py").is_file()
                assert not (Path('.') / 'BAR' / 'tests' / 'bar' / f"test_cli_{component_new_name}.py").is_file()
            else:
                assert not (Path('.') / 'BAR' / 'bar' / component_new_name).is_dir()
                assert not (Path('.') / 'BAR' / 'tests' / 'bar' / component_new_name).is_dir()

        print('ok')

def test_rename_remove_2():
    """test rename and remove of sub-submodules"""
    with utils.in_directory(helpers.test_workspace()):
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').exists()
        # add Python submodule 'foo'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo').is_dir()
        # add Python submodule 'foo/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/soup', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'soup').is_dir()
        # rename bar/foo/soup -> bar/foo/onion_aoup
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/soup', 'onion_soup']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'onion_soup').is_dir()
        # remove foo/onion_soup (keep foo)
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/onion_soup']))
        assert not (Path('.') / 'BAR' / 'bar' / 'foo'/ 'onion_soup').is_dir()


def test_rename_remove_3():
    """test rename and remove of submodules with sub-submodules"""
    with utils.in_directory(helpers.test_workspace()):
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').exists()
        # add Python submodule 'foo'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo').is_dir()
        # add Python submodule 'foo/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/soup', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'soup').is_dir()
        # rename bar/foo -> bar/foo2
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo', 'foo2']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo2'/ 'soup').is_dir()
        # remove bar/foo2 and bar/foo2/soup
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo2']))
        assert not (Path('.') / 'BAR' / 'bar' / 'foo2'/ 'soup').is_dir()
        assert not (Path('.') / 'BAR' / 'bar' / 'foo2').is_dir()


def test_move_1():
    """test move of sub-submodules between submodules"""
    with utils.in_directory(helpers.test_workspace()):
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').is_file()
        # add Python submodule 'foo'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo').is_dir()
        # add Python submodule 'foo/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/soup', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'soup').is_dir()
        # add Python submodule 'foo2'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo2', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo2').is_dir()
        # add Python submodule 'foo/sub'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/sub', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo' / 'sub').is_dir()
        # rename soup -> onion_soup
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/soup', 'onion_soup']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'onion_soup').is_dir()
        # move onion_soup from foo to foo2
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/onion_soup', 'foo2']))
        assert not (Path('.') / 'BAR' / 'bar' / 'foo' / 'onion_soup').is_dir()
        assert     (Path('.') / 'BAR' / 'bar' / 'foo2'/ 'onion_soup').is_dir()
        # move onion_soup from foo2 to foo/sub
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo2/onion_soup', 'foo/sub']))
        assert not (Path('.') / 'BAR' / 'bar' / 'foo2' / 'onion_soup').is_dir()
        assert     (Path('.') / 'BAR' / 'bar' / 'foo'  / 'sub' / 'onion_soup').is_dir()

def test_similar():
    """"""
    with utils.in_directory(helpers.test_workspace()):
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').is_file()
        # add Python submodule 'foo'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo').is_dir()
        # add Python submodule 'foo/soup'
        results.append(helpers.micc(['-p', 'BAR', 'add', 'foo/soup', '--py']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'soup').is_dir()
        # remove soup but pass the wrong path
        with pytest.raises(AssertionError):
            results.append(helpers.micc(['-p', 'BAR', 'mv', 'soup']))


if __name__ == "__main__":
    the_test_you_want_to_debug = test_similar

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
