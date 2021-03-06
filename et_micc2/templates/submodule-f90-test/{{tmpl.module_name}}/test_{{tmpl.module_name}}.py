#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for f90 module `{{tmpl.package_name}}.{{tmpl.module_name}}`."""

import {{tmpl.package_name}}
# create an alias for the binary extension cpp module
f90 = {{tmpl.package_name}}.{{tmpl.module_name}}

import numpy as np


def test_f90_add():
    x = np.array([0,1,2,3,4],dtype=float)
    shape = x.shape
    y = np.ones (shape,dtype=float)
    z = np.zeros(shape,dtype=float)
    expected_z = x + y
    f90.add(x,y,z)
    assert (z == expected_z).all()

#===============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
#===============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_f90_add

    print(f"__main__ running {the_test_you_want_to_debug} ...")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
#===============================================================================
