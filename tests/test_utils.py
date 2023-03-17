#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for utils module."""

from pathlib import Path
import semantic_version as sv
import sys

import et_micc2.tools.utils as utils
from tests import helpers

sys.path.insert(0,'.')
sys.path.insert(0,'..')

def test_version_range():
    vs = "1.2.3"
    vv = sv.Version(vs)
    vn = vv.next_patch()
    
    vc = f"=={vs}"
    bounds = utils.version_range(vc)
    assert bounds[0] == vv
    assert bounds[1] == sv.Version("1.2.4")

    vc = f">={vs}"
    bounds = utils.version_range(vc)
    assert bounds[0] == vv
    assert bounds[1] is None

    vc = f">{vs}"
    bounds = utils.version_range(vc)
    assert bounds[0] == vn
    assert bounds[1] is None

    vc = f"<={vs}"
    bounds = utils.version_range(vc)
    assert bounds[0] is None
    assert bounds[1] == vn

    vc = f"<{vs}"
    bounds = utils.version_range(vc)
    assert bounds[0] is None
    assert bounds[1] == vv
    
    vc = f"^{vs}"
    vu = sv.Version("2.0.0")
    bounds = utils.version_range(vc)
    assert bounds[0] == vv
    assert bounds[1] == vu


def test_convert_caret_specification():
    spec = ">=1.1.2"
    assert utils.convert_caret_specification(spec) == spec
    spec = "^1.1.2"
    spec_new = utils.convert_caret_specification(spec)
    assert spec_new == ">=1.1.2,<2.0.0"
    assert     sv.SimpleSpec("1.1.2").match(sv.Version("1.1.2"))
    assert not sv.Version("1.1.1") in sv.SimpleSpec(spec_new)
    assert     sv.Version("1.1.2") in sv.SimpleSpec(spec_new)
    assert     sv.Version("1.1.2") in sv.SimpleSpec(spec_new)
    assert     sv.Version("1.2.2") in sv.SimpleSpec(spec_new)
    assert not sv.Version("2.0.0") in sv.SimpleSpec(spec_new)
    assert not sv.Version("2.2.2") in sv.SimpleSpec(spec_new)


def test_verify_project_name():
    assert not utils.verify_project_name("1")
    assert not utils.verify_project_name("1ab")
    assert utils.verify_project_name("a")
    assert utils.verify_project_name("a1")
    assert utils.verify_project_name("a123b")
    assert utils.verify_project_name("a_-123b")
    assert utils.verify_project_name("A_-123B")
    assert not utils.verify_project_name("A_-123.B")
    assert not utils.verify_project_name("A._-123.B")
    assert not utils.verify_project_name("A_-123 B")
    
def test_insert_in_file():
    with helpers.in_empty_tmp_dir():
        file = Path('test.txt')
        with file.open(mode='w') as f:
            for i in range(10):
                f.write(str(i) + '\n')
        ilines = ["insert 1","insert 2"]
        utils.insert_in_file(file, ilines, before=True, startswith="5")
        with file.open() as f:
            lines = f.readlines()
            for l,line in enumerate(lines):
                print(line)
                if l==5:
                    assert line.startswith(ilines[0])
                if l==6:
                    assert line.startswith(ilines[1])

        file = Path('test.txt')
        with file.open(mode='w') as f:
            for i in range(10):
                f.write(str(i) + '\n')
        ilines = ["insert 1","insert 2"]
        utils.insert_in_file(file, ilines, before=False, startswith=("5"))
        with file.open() as f:
            lines = f.readlines()
            for l,line in enumerate(lines):
                print(line)
                if l==6:
                    assert line.startswith(ilines[0])
                if l==7:
                    assert line.startswith(ilines[1])


def test_in_directory():

    helpers.clear_test_workspace()
    p0 = Path.cwd()

    pFoo = helpers.test_workspace / 'Foo'
    pFoo.mkdir()
    try:
        with utils.in_directory(pFoo):
            assert Path.cwd() == pFoo
            print(f'cwd = {pFoo}')
            raise RuntimeError
    except:
        print(f'except: cwd = {Path.cwd()}')
        assert Path.cwd() == p0
    helpers.clear_test_workspace()


# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_in_directory

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
# ==============================================================================
