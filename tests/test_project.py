#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `micc` package."""
from types import SimpleNamespace
from pathlib import Path

from et_micc2.project import Project, ToolInfo

def test_ctor():
    options = SimpleNamespace(
        project_path=Path.cwd(),
        template_parameters={},
        verbosity=3,
        clear_log=False,
    )
    proj = Project(options)
    print(proj.pyproject_toml['tool']['poetry']['dependencies'])


def test_existing_tool():
    ti = ToolInfo('gh')
    assert ti.is_available()

def test_inexisting_tool():
    ti = ToolInfo('ghh')
    assert not ti.is_available()
    if not ti.is_available():
        print('The ghh command is not available in your environment.\n'
                     'If you continue this project a remote repository will not be created.'
                     )
        answer = input('Continue? [Yes]/No')
        if answer.lower().startswith('n'):
            print('Project not created.')
        else:
            print('continuing')


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_inexisting_tool

    the_test_you_want_to_debug()
    print('-*# finished #*-')
# ==============================================================================
