#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

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
                assert (Path('.') / 'BAR' / 'bar' / f"cli_{component_name}.py").is_file()
            else:
                assert (Path('.') / 'BAR' / 'bar' / component_name).is_dir()

        # rename components submod -> foo
        for flag in component_flags:
            component_name  = f"submod_{flag[2:]}"
            component_new_name = f'foo_{flag[2:]}'
            results.append(helpers.micc(['-p', 'BAR', 'mv', component_name, component_new_name]))
            if 'cli' in flag:
                assert (Path('.') / 'BAR' / 'bar' / f"cli_{component_new_name}.py").is_file()
                assert (Path('.') / 'BAR' / 'tests' / 'bar' / f"test_cli_{component_new_name}.py").is_file()
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
        component_flags = ['--py', '--f90', '--cpp']
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
        # rename
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/soup', 'onion_soup']))
        assert (Path('.') / 'BAR' / 'bar' / 'foo'/ 'onion_soup').is_dir()
        # rename
        results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo/onion_soup']))
        assert not (Path('.') / 'BAR' / 'bar' / 'foo'/ 'onion_soup').is_dir()


if __name__ == "__main__":
    the_test_you_want_to_debug = test_rename_remove_1

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
