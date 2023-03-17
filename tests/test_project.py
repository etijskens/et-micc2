#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `micc` package."""
from pathlib import Path
from types import SimpleNamespace

import et_micc2.tools.env as env
import et_micc2.tools.project as project

def test_ctor():
    options = SimpleNamespace(
        project_path=Path.cwd(),
        template_parameters={},
        verbosity=3,
        clear_log=False,
        preferences = {}
    )
    proj = project.Project(options)
    print(proj.pyproject_toml['tool']['poetry']['dependencies'])


def test_existing_tool():
    ti = env.ToolInfo('gh')
    assert ti.is_available()

def test_inexisting_tool():
    ti = env.ToolInfo('ghh')
    assert not ti.is_available()
    if not ti.is_available():
        print('The ghh command is not available in your environment.\n'
                     'If you continue this project a remote repository will not be created.'
                     )
        # answer = input('Continue? [Yes]/No')
        answer = 'no'
        if answer.lower().startswith('n'):
            print('Project not created.')
        else:
            print('continuing')


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_ctor

    the_test_you_want_to_debug()
    print('-*# finished #*-')
# ==============================================================================
