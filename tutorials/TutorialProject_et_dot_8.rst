.. include:: ../HYPERLINKS.rst

.. _python-submodules:

4. Adding Python submodules
===========================

Adding binary extension (sub)modules is important for adding implementations in
Fortran or C++ for performance reasons. For larger projects it is sometimes
practical to be able to organize your Python code in different files, e.g. one file for
each Python class. Micc2_ allows your to add Python submodules to your project. Just
as the default top level package, these Python submodules have a package structure
too. This command adds a module :file:`foo.py` to your project:

.. code-block:: 

    micc2 add foo --py
    [INFO]           [ Adding python submodule foo to package et_dot.
    [INFO]               - python source in    /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/foo/__init__.py.
    [INFO]               - Python test code in /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/tests/et_dot/foo/test_foo.py.
    [INFO]           ] done.
    

We can add sub-submodules too. E.g to add a ``bar`` sub-module to the ``foo``
sub-module:

.. code-block:: 

    micc2 add foo/bar --py
    [INFO]           [ Adding python submodule foo/bar to package et_dot.
    [INFO]               - python source in    /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/foo/bar/__init__.py.
    [INFO]               - Python test code in /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/tests/et_dot/foo/bar/test_bar.py.
    [INFO]           ] done.
    

In fact this sub-sub-module ``bar`` can even be a C++ of Fortran binary extension
module. One only needs to replace the ``--py`` flagwith ``--cpp`` or ``--f90``. The
binary extension modules themselves, however, cannot contain submodules.

As usual, Micc2_ added example code and example test code for the added components. as
well as documentation entries for the submodule.

.. _clis:

4.1. Adding a Python Command Line Interface
-------------------------------------------

*Command Line Interfaces* are Python scripts in a Python package that are
installed as executable programs when the package is installed.  E.g. Micc2_ is a CLI.
Installing package :file:`et-micc2` installs the ``micc2`` as an executable
program. CLIs come in two flavors, single command CLIs and CLIs with subcommands.
Single command CLIs perform a single task, which can be modified by optional
parameters and flags. CLIs with subcommands can performs different, usually
related, tasks by selecting an appropriate subcommand. Git_ and Micc2_ are CLIs with
subcommands. You can add a single command CLI named ``myapp`` to your project with the
command:

.. code-block:: bash

    > micc2 add myapp --cli

and

.. code-block:: bash

    > micc2 add myapp --clisub

for a CLI with subcommands. Micc2 adds the necessary files, containing working
example code and tests, as well as a documentation entry in :file:`APPS.rst`. The
documentation will be extracted automatically from doc-strings and help-strings
(these are explained below). 

.. _cli-example:

4.1.1. CLI example
^^^^^^^^^^^^^^^^^^

Assume that we need quite often to read two arrays from file and compute their dot
product, and that we want to execute this operation as:

.. code-block:: bash

    > dotfiles file1 file2
    dot(file1,file2) = 123.456

The second line is the output that we expect.

:file:`dotfiles` is, obviously a single command CLI, so we add a CLI component with
the ``--cli`` flag:

.. code-block:: 

    micc2 add dotfiles --cli
    [INFO]           [ Adding CLI dotfiles to project ET-dot
                            (single command CLI).
    [INFO]               - Python source file ET-dot/et_dot/cli_dotfiles.py.
    [INFO]               - Python test code   ET-dot/tests/test_cli_dotfiles.py.
    [WARNING]            Dependencies added:
                         If you are using a virtual environment created with poetry, run:
                             `poetry install` or `poetry update` to install missing dependencies.
                         If you are using a virtual environment not created with poetry, run:
                             (.venv) > pip install click
                         Otherwise, run:
                             > pip install click --user
    [INFO]           ] done.
    

As usual Micc2 tells us where to add the source code for the CLI, and where to add the test
code for it. Furthermore, Micc2_ expects us to use the Click_ package for
implementing the CLI, a very practical and flexible package which is well
documented. The example code in :file:`et_dot/cli_dotfiles.py` is already based
on Click_, and contains an example of a single command CLI or a Cli with subcommands,m
depending on the flag you used. Here is the proposed implementation of our
:file:`dotfiles` CLI:

.. code-block:: python

    # -*- coding: utf-8 -*-
    """Command line interface dotfiles (no sub-commands)."""
    
    import sys
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

Click_ uses decorators to add arguments and options to turn a method, here
:file:`main()` in to the command. Understanding decorators is not really
necessary, but if you are intrigued, check out
`Primer on Python decorators <https://realpython.com/primer-on-python-decorators/>`_.
Otherwise, just follow the Click_ documentation for how to use the Click_ decorators
to create nice CLIs. 

.. code-block:: 

    1,2,3

.. code-block:: 

    4,5,6

Click_ provides a lot of practical features, such as an automatic help function which
is built from the doc-string of the command method, and the ``help`` parameters of the
options. Sphinx_click_ does the same to extract documentation for your CLI.

.. code-block:: bash

    > python et_dot/cli_dotfiles.py --help
    Usage: cli_dotfiles.py [OPTIONS] FILE1 FILE2
    
      Command line interface dot-files, computes the dot product of two arrays
      in files ``file1`` and ``file2`` and prints the result.
    
      file format is text, comma delimited
    
      :param str file1: location of file containing first array :param str
      file2: location of file containing first array
    
    Options:
      -v, --verbosity  The verbosity of the CLI.
      --help           Show this message and exit.
    
    > python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt
    32.0
    
    > python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt -v
    dotfiles([1. 2. 3.],[4. 5. 6.]) = 32.0
    
    > python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt -vv
    a <- tests/array1.txt
    b <- tests/array2.txt
    dotfiles([1. 2. 3.],[4. 5. 6.]) = 32.0
    

Here, we did not exactly call the CLI as ``dotfiles``, but that is because the package
is not yet installed. The installed executable ``dotfiles`` would just wrap the
command as ``python path/to/et_dot/cli_dotfiles.py``. Note, that the verbosity
parameter is using a nice Click_ feature: by adding more ``v`` s the verbosity
increases.

