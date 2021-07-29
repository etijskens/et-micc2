# -*- coding: utf-8 -*-

"""Tests for tmpl package."""
import shutil

import et_micc2.tmpl

from pathlib import Path
import pytest

def test_expand_string():
    s = "This is {{tmpl.bar}} and this is {{tmpl.foo}}.\nAnd this is {{tmpl.foobar}}."
    parameters = { 'foo':'expanded_foo'}
    with pytest.raises(ValueError):
        s = et_micc2.tmpl.expand_string(s,parameters)
    parameters = { 'foo':'expanded_foo', 'bar':'expanded_bar', 'foobar':'expanded_foobar'}
    s = et_micc2.tmpl.expand_string(s, parameters)
    assert s == 'This is expanded_bar and this is expanded_foo.\nAnd this is expanded_foobar.'


def test_expand_file():
    root = Path('./tests')
    path_to_template = root / 'template_file_{{tmpl.fname}}'
    assert path_to_template.exists()

    destination = Path("./tests/expanded_file")
    destination.mkdir(exist_ok=True)
    (destination / 'template_file_expanded_template').unlink(missing_ok=True)

    parameters = { 'foo':'expanded_foo'
                 , 'bar':'expanded_bar'
                 , 'foobar':'expanded_foobar'
                 }
    with pytest.raises(ValueError):
        et_micc2.tmpl.expand_file(root, path_to_template, destination, parameters)

    parameters['fname'] = 'expanded_template'
    assert et_micc2.tmpl.expand_file(root, path_to_template, destination, parameters) is None

    f = (destination / 'template_file_expanded_template')
    assert f.is_file()

    s = f.read_text()
    assert s == 'This is expanded_bar and this is expanded_foo.\nAnd this is expanded_foobar.'


def test_expand_folder():
    path_to_template = Path("./tests/template_folder_{{tmpl.dname}}")
    assert path_to_template.exists()

    destination = Path("./tests/expanded_folder")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(exist_ok=True)

    parameters = { 'foo':'expanded_foo'
                 , 'bar':'expanded_bar'
                 , 'foobar':'expanded_foobar'
                 , 'dname':'expanded_dname'
                 , 'fname':'expanded_fname'
                 , 'dnamesub':'expanded_dnamesub'
                 }

    et_micc2.tmpl.expand_folder(path_to_template, destination, parameters)

    assert (destination / 'template_folder_expanded_dname').is_dir()
    assert (destination / 'template_folder_expanded_dname/template_file_expanded_fname').is_file()
    assert (destination / 'template_folder_expanded_dname/template_subfolder_expanded_dnamesub').is_dir()
    assert (destination / 'template_folder_expanded_dname/template_subfolder_expanded_dnamesub/sub_template_file_expanded_fname').is_file()
    expected = "This is expanded_bar and this is expanded_foo.\nAnd this is expanded_foobar."
    assert (destination / 'template_folder_expanded_dname/template_file_expanded_fname').read_text() == expected
    assert (destination / 'template_folder_expanded_dname/template_subfolder_expanded_dnamesub/sub_template_file_expanded_fname').read_text() == expected

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (otherwise all tests are normally run with pytest)
# Make sure that you run this code with the project directory as CWD, and
# that the source directory is on the path
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_expand_folder

    print("__main__ running", the_test_you_want_to_debug)
    the_test_you_want_to_debug()
    print('-*# finished #*-')
    
# eof