# -*- coding: utf-8 -*-

"""Tests for tmpl package."""

import tmpl

from pathlib import Path
import pytest

def test_expand():
    """Test for tmpl.expand"""
    path_to_template = Path("./tests/template")
    assert path_to_template.exists()

    destination = Path("./tests/expanded")
    destination.mkdir(exist_ok=True)
    (destination / 'template').unlink(missing_ok=True)

    parameters = { 'foo':'expanded_foo'
                 , 'bar':'expanded_bar'
                 }
    with pytest.raises(ValueError):
        tmpl.expand(path_to_template, destination, parameters) == 'foobar'
    parameters['foobar'] = 'foobar_expanded'
    assert tmpl.expand(path_to_template, destination, parameters) is None
    s = (destination/'template').read_text()
    assert s == 'This is expanded_bar and this is expanded_foo.\nAnd this is foobar_expanded.'

def test_expand_filename():
    """Test for tmpl.expand"""
    path_to_template = Path("./tests/{{tmpl.filename}}")
    assert path_to_template.exists()

    destination = Path("./tests/expanded")
    destination.mkdir(exist_ok=True)
    (destination / 'template').unlink(missing_ok=True)

    parameters = { 'foo':'expanded_foo'
                 , 'bar':'expanded_bar'
                 }
    with pytest.raises(ValueError):
        tmpl.expand(path_to_template, destination, parameters)

    parameters['foobar'] = 'foobar_expanded'
    with pytest.raises(ValueError):
        tmpl.expand(path_to_template, destination, parameters)

    parameters['filename'] = 'template_expanded'

    assert tmpl.expand(path_to_template, destination, parameters) is None

    s = (destination/'template_expanded').read_text()
    assert s == 'This is expanded_bar and this is expanded_foo.\nAnd this is foobar_expanded.'


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_expand_filename

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')
    
# eof