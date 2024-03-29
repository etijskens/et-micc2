#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `{{tmpl.project_name}}.{{tmpl.app_name}} ` CLI."""

import pytest

from click.testing import CliRunner
from click import echo

from click.testing import CliRunner

from {{tmpl.package_name}}.cli.{{tmpl.app_name}} import main


def test_hello():
    runner = CliRunner()
    result = runner.invoke(main, ['-vv','hello'])
    print(result.output)
    assert 'Hello world' in result.output


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_hello

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
# eof
