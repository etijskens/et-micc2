# -*- coding: utf-8 -*-
"""Command line interface dotfiles (no sub-commands)."""

import sys
sys.path.insert(0,'.')      #hide#
import click
import numpy as np
import et_dot

@click.command()
@click.argument('file1')
@click.argument('file2')
@click.option('-v', '--verbosity', count=True
    , help="The verbosity of the CLI."
    , default=0
)
def main(file1, file2, verbosity):
    """Command line interface dot-files, computes the dot product of two arrays
    in files ``file1`` and ``file2`` and prints the result.

    file format is text, comma delimited

    :param str file1: location of file containing first array
    :param str file2: location of file containing first array
    """
    # Read the arrays from file, assuming comma delimited
    a = np.genfromtxt(file1, dtype=np.float64, delimiter=',')
    b = np.genfromtxt(file2, dtype=np.float64, delimiter=',')
    # Sanity check:
    if len(a) != len(b): raise ValueError
    # Using the C++ dot product implementation:
    ab = et_dot.dotc.dot(a,b)
    if verbosity:
        if verbosity>1:
            print(f"a <- {file1}")
            print(f"b <- {file2}")
        print(f"dotfiles({a},{b}) = {ab}")
    else:
        print(ab)
    return 0 # return code

if __name__ == "__main__":
    sys.exit(main())
