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

def test_add_cli():
    """test add cli components"""
    with utils.in_directory(helpers.test_workspace()):
        component_flags = ['--cli', '--clisub']
        results = []
        # Create package BAR
        results.append(helpers.micc(['-p', 'BAR', 'create', '--allow-nesting', '--remote=none']))
        assert Path('BAR/bar/__init__.py').exists()
        # add cli component 'app' for every different component flag
        for flag in component_flags:
            component_name = f"app_{flag[2:]}"
            results.append(helpers.micc(['-p', 'BAR', 'add', component_name, flag]))
            assert (Path('.') / 'BAR' / 'bar' / 'cli' / f"{component_name}.py").is_file()
        results.append(helpers.micc(['-p', 'BAR', 'doc']))


if __name__ == "__main__":
    the_test_you_want_to_debug = test_add_cli

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
