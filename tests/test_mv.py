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

def test_rename_project():
    helpers.clear_test_workspace()

    with utils.in_directory(helpers.test_workspace):
        results = []
        # Create package BAR
        result = helpers.micc(['-vv', '-p', 'BAR', 'create', '--allow-nesting', '--remote=none'])
        assert Path('BAR/bar/__init__.py').exists()
        results.append(result)

        result = helpers.micc(['-vvv', '-p', 'BAR', 'info'])
        results.append(result)

        with utils.in_directory('BAR'):
            completed_process = subprocess.run(['pytest', 'tests/bar'])
            assert completed_process.returncode == 0
            # Add a python sub-module
            submodule = 'submodule_py'
            result = helpers.micc(['-v', 'add', submodule, '--py'])

            completed_process = subprocess.run(['pytest', 'tests/bar/'])
            assert completed_process.returncode == 0

            # Add a binary sub-module
            for flag in ['--cpp', '--f90']:
                submodule = f'submodule_{flag[2:]}'
                result = helpers.micc(['-v', 'add', submodule, flag])
                # test micc build
                if flag == '--f90' and __skip_build_f90__:
                    print('skipping build f90 because f2py is missing.')
                    continue
                # We are relying on automatic build here. This also tests the `micc build` command
                completed_process = subprocess.run(['pytest', 'tests/bar/'])

                extension_suffix = build.get_extension_suffix()
                binary_extension = Path(f'bar/{submodule}{extension_suffix}')
                assert binary_extension.exists()

            for cli, cli_flag in zip(['clibar', 'clibarsup'], ['--cli', '--clisub']):
                result = helpers.micc(['-v', 'add', cli, cli_flag])
                completed_process = subprocess.run(['pytest', 'tests/bar/'])
                assert completed_process.returncode == 0

            if 'VSC_HOME' in os.environ:
                print('Not testing build documentation')
            else:
                # test building documentation
                with utils.in_directory('docs'):
                    completed_process = subprocess.run(['make', 'html'])
                    assert completed_process.returncode == 0


if __name__ == "__main__":
    the_test_you_want_to_debug = test_rename_project

    print(f"{__file__}::__main__ executing test '{the_test_you_want_to_debug}'")
    the_test_you_want_to_debug()

    print('-*# finished #*-')
