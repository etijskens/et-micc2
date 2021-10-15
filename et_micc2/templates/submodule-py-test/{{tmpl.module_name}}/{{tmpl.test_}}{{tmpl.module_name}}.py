#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for sub-module {{tmpl.import_lib}}."""

import pytest
import {{tmpl.import_lib}}


def test_greet():
    expected = "Hello John!"
    greeting = {{tmpl.package_name}}.{{tmpl.module_name}}.greet("John")
    assert greeting==expected


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_greet

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print("-*# finished #*-")
# ==============================================================================
