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

        # rename submod -> foo
        for flag in component_flags:
            component_name  = f"submod_{flag[2:]}"
            component_new_name = f'foo_{flag[2:]}'
            results.append(helpers.micc(['-p', 'BAR', 'mv', component_name, component_new_name]))
            if 'cli' in flag:
                assert (Path('.') / 'BAR' / 'bar' / f"cli_{component_new_name}.py").is_file()
            else:
                assert (Path('.') / 'BAR' / 'bar' / component_new_name).is_dir()



        # delete foo
        # results.append(helpers.micc(['-p', 'BAR', 'mv', 'foo']))
        # assert (Path('.') / 'BAR' / 'bar'  / 'foo' / '__init__.py').is_file()

        print('ok')


if __name__ == "__main__":
    the_test_you_want_to_debug = test_rename_remove_1

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
