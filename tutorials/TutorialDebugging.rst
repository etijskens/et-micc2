.. include:: ../HYPERLINKS.rst

8. Debugging binary extensions
==============================

Debugging is the process of executing a program step by step, in order to discover
where and why it goes wrong. It is an indispensable step in software development.
Although tests may tell you what part of your code fails, but the origin of the failure
is not always clear. As explained in the tutorials (see :ref:`testing-your-code`)
unit tests are useful for two reasons:

#. they assure that your code does not get broken while you add features, or modify it, and

#. they constrain the part of the code that has an issue. If a test fails, the origin of the
   must be somewhere in the part of the code that is tested. By keeping the tested parts
   small, you will find the flaw sooner, and proceed faster. 

For small projects inserting print statements in flawed code can be a good approach to
discover the flaw, but it is cumbersome and in the case of binary extensions requires
rebuilding the code often. Debugging is a more scalable approach. 

Graphical Debuggers as provided in IDEes, e.g. PyCharm, Eclipse_ + pydev_, Visual
Studio, present a great user experience, but not all are capable of debugging mixed
Python/C++/Fortran. See
`here <https://wiki.python.org/moin/IntegratedDevelopmentEnvironments>`_
for more information.

* Pycharm_: only Python, but great user experience.

* eclipse: debugging binaries should be possible but not really mixed mode.

* Visual Studio code: provides mixed language debugging Python/C++/Fortran.

.. note::

   June 8, 2021: On MACOS, Visual Studio Code, as it uses lldb under the hood, also does not
   show the variables in a Fortran binary extension. It is unclear whether that is due to a
   quirk in f2py or lldb.

For HPC environments there is also:

* `Arm DDT <https://www.arm.com/products/development-tools/server-and-hpc/forge/ddt>`_

* `TotalView HPC Debugging Software <https://totalview.io/products/totalview>`_

These are also capable debugging OpenMP (multi-threaded) and MPI applications
(multi-process).

For Linux environments there is also a lightweight approach possible using gdb_ and
pdb_. On MACOS gdb_ can be replaced by lldb_, which has very similar features, but
different commands. (At the time of writing gdb_ for MACOS was broken). Here are two
links describing the approach:

#. https://www.researchgate.net/figure/Debugging-both-C-extensions-and-Python-code-with-gdb-and-pdb_fig2_220307949

#. https://www.boost.org/doc/libs/1_76_0/libs/python/doc/html/faq/how_do_i_debug_my_python_extensi.html

The first link describes a fully mixed Python C++ approach, and works for Fortran as
well. Thesecond link, is semi-mixed. It expects you to enter the Python commands
yourself, which may be tedious at times, but can be practical to explore the
situation.

We illustrate both strategies using a project foo with a C++ binary extension
``cxx``, and a Fortran binary extension ``fortran``. The code we are using is just the
example code created by micc2_, which defines a function for adding to arrays. 

.. code-block:: 

    > micc2 create foo --package
    ...
    > micc2 add cxx --cpp
    ...
    > micc2 add fortran --f90
    ...
    > micc2 info
    Project foo located at /Users/etijskens/software/dev/workspace/foo
      package: foo
      version: 0.0.0
      structure: foo/__init__.py (Python package)
      contents:
        C++ module  cpp_cxx/cxx.cpp
        f90 module f90_fortran/fortran.f90
    micc2 build --build-type Debug
    ...

Make sure that you pass the ``--build-type Debug`` flag, so that the binary
extensions are built with debug information.

It is recommend to debug small scripts, rather than complete applications. This is,
however, not always possible.

8.1. Mixed Python/C++ debugging with lldb and pdb
-------------------------------------------------

This section illustrates mixed language debugging of a Python script calling a
method from a C++ binary extension. Here we are using ``lldb`` on a MACOS system. In the
next section we will do the same for a Fortran binary extension on Linux (Ubuntu),
using ``gdb``.

.. note::

   For an overview of ``lldb`` checkout https://lldb.llvm.org.

.. note::

   For an overview of ``pdb`` checkout
   https://docs.python.org/3/library/pdb.html, and
   `Python Debugging With Pdb <https://realpython.com/python-debugging-pdb/>`_.
   

Suppose we are concerned about the C++ correctness of the ``add`` function and that we
want to execute it step by step to see if it runs as expected. We first demonstrate the
approach of the first link above, on MACOS, using lldb_ instead of gdb_. The commands
are different for ``gdb`` and ``lldb``, but the strategy is exactly the same. First,
start lldb_ with the Python executable you want to use. As I am using pyenv_ to manage
differen python versions on my machine, the ``python`` on the PATH is only a wrapper
for the the real Python executable, so I must specify the full path, because ``lldb``
expects a true executable.

.. code-block:: 

    > lldb ~/.pyenv/versions/3.8.5/bin/python
    (lldb) target create "/Users/etijskens/.pyenv/versions/3.8.5/bin/python"
    Current executable set to '/Users/etijskens/.pyenv/versions/3.8.5/bin/python' (x86_64).
    (lldb) target create "/Users/etijskens/.pyenv/versions/3.8.5/bin/python"
    (lldb)

Next, you set a breakpoint in the c++ file, e.g. on the first line of the ``add``
function. As the binary extension, which is in fact nothing else than a dynamic
library, has not been loaded yet, ``lldb`` replies that there is no location for the
breakpoint, and that the breakpoint is 'pending', i.e. waiting to become active as
soon as the dynamic library is loaded.

.. code-block:: 

    (lldb) breakpoint set --file cxx.cpp -l 19
    Breakpoint 1: no locations (pending).
    WARNING:  Unable to resolve breakpoint to any actual locations.
    (lldb)

Next, start the Python test script for the C++ add function,
:file:`tests	est_cpp_cxx.py` with ``pdb``:

.. code-block:: 

    (lldb) run -m pdb tests/test_cpp_cxx.py
    Process 26917 launched: '/Users/etijskens/.pyenv/versions/3.8.5/bin/python' (x86_64)
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(4)<module>()
    -> """
    (Pdb)

and set a ``pdb`` breakpoint on the test method for the ``add`` function (which is
called in the ``if __name__ == "__main__":`` body: 

.. code-block:: 

    (Pdb) b test_cpp_add
    Breakpoint 1 at /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py:19
    (Pdb)

This time the breakpoint is found right away, because the file that contains it,
``tests/test_cpp_cxx.py`` is already loaded. 

Now we are ready to start the script with the ``r(un)`` command, after which ``pbd``
stops at the first line in the test_cpp_add method, the ``pdb`` breakpoint:

.. code-block:: 

    (Pdb) r
    1 location added to breakpoint 1
    __main__ running <function test_cpp_add at 0x104890310> ...
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(20)test_cpp_add()
    -> x = np.array([0,1,2,3,4],dtype=float)
    (Pdb)

Now, we can execute this line and inspect the variable ``x`` with the ``p(rint)``
command:

.. code-block:: 

    (Pdb) n
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(21)test_cpp_add()
    -> shape = x.shape
    (Pdb) p x
    array([0., 1., 2., 3., 4.])
    (Pdb)

Continue stepping until you arrive at the call to ``cpp.add``, you can examine de
contents of ``y`` and ``z`` as well, just as every other variable which is in the scope:

.. code-block:: 

    (Pdb) n
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(22)test_cpp_add()
    -> y = np.ones (shape,dtype=float)
    (Pdb) n
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(23)test_cpp_add()
    -> z = np.zeros(shape,dtype=float)
    (Pdb) n
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(24)test_cpp_add()
    -> expected_z = x + y
    (Pdb) n
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(25)test_cpp_add()
    -> result = cpp.add(x,y,z)
    (Pdb) p y
    array([1., 1., 1., 1., 1.])
    (Pdb) p z
    array([0., 0., 0., 0., 0.])
    (Pdb)

Stepping once more will hit the breakpoint on linr 19 of file ``cxx.cpp`` in ``lldb``:

.. code-block:: 

    (Pdb) n
    Process 26917 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
        frame #0: 0x0000000112324b58 cxx.cpython-38-darwin.so`add(x=array_t<double, 16> @ 0x00007ffeefbfc3a8, y=array_t<double, 16> @ 0x00007ffeefbfc3a0, z=array_t<double, 16> @ 0x00007ffeefbfc388) at cxx.cpp:19:19
       16  	    , py::array_t<double> z
       17  	    )
       18  	{
    -> 19  	    auto bufx = x.request()
       20  	       , bufy = y.request()
       21  	       , bufz = z.request()
       22  	       ;
    Target 0: (python) stopped.
    (lldb)

as in pdb you can execute step by step with the ``n(ext)`` command. Continue stepping
until you arrive at line 38, where you can examine the contents of the x argument.

.. code-block:: 

    (lldb) n
    Process 26917 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = step over
        frame #0: 0x0000000112324d80 cxx.cpython-38-darwin.so`add(x=array_t<double, 16> @ 0x00007ffeefbfc3a8, y=array_t<double, 16> @ 0x00007ffeefbfc3a0, z=array_t<double, 16> @ 0x00007ffeefbfc388) at cxx.cpp:38:59
       35  	 // because the Numpy arrays are mutable by default, py::array_t is mutable too.
       36  	 // Below we declare the raw C++ arrays for x and y as const to make their intent clear.`
       37  	    double const *ptrx = static_cast<double const *>(bufx.ptr);
    -> 38  	    double const *ptry = static_cast<double const *>(bufy.ptr);
       39  	    double       *ptrz = static_cast<double       *>(bufz.ptr);
       40
       41  	    for (size_t i = 0; i < bufx.shape[0]; i++)~ 
    Target 0: (python) stopped.
    (lldb) p ptrx[0]
    (const double) $0 = 0
    (lldb) p ptrx[1]
    (const double) $1 = 1
    (lldb)

You can continue to execute line by line, which will eventually drop you in the wrapper
code, which is hard to understand and not necessarily compiled with debugging
information. We step out of it with the ``finish`` command, to end up back in ``pdb``:

.. code-block:: 

    (lldb) finish
    > /Users/etijskens/software/dev/workspace/foo/tests/test_cpp_cxx.py(26)test_cpp_add()
    -> assert (z == expected_z).all()
    (Pdb)

8.2. Mixed Python/Fortran debugging with gdb and pdb on Linux
-------------------------------------------------------------

This time we will debug the ``tests/test_f90_fortran.py`` script which calls the
Fortran binary extension.We are using gdb from an Ubuntu machine.

.. note::

   For an overview of ``gdb`` checkout
   https://www.gnu.org/software/gdb/documentation/.

.. note::

   For an overview of ``pdb`` checkout
   https://docs.python.org/3/library/pdb.html, and
   `Python Debugging With Pdb <https://realpython.com/python-debugging-pdb/>`_.
   

As above we start the true Python executable, but this time with ``gdb``. The
procedure is very similar. Only the ``gdb`` commands differ a somewhat from thee
``lldb`` commands, and sometimes the output is different too.

.. code-block:: 

    osboxes@osboxes:~/workspace/foo$ gdb ~/.pyenv/versions/3.9.5/bin/python
    GNU gdb (Ubuntu 10.1-2ubuntu2) 10.1.90.20210411-git
    Copyright (C) 2021 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it. 
    There is NO WARRANTY, to the extent permitted by law. 
    Type "show copying" and "show warranty" for details.
    This GDB was configured as "x86_64-linux-gnu".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    <https://www.gnu.org/software/gdb/bugs/>.
    Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.
    
    For help, type "help".
    Type "apropos word" to search for commands related to "word"...
    Reading symbols from /home/osboxes/.pyenv/versions/3.9.5/bin/python...
    (gdb) b fortran.f90:32
    No source file named fortran.f90.
    Make breakpoint pending on future shared library load? (y or [n]) y
    Breakpoint 1 (fortran.f90:32) pending.

``Gdb`` asks you to confirm if you set a breakpoint that cannot be found yet.

.. code-block:: 

    (gdb) run -m pdb tests/test_f90_fortran.py
    Starting program: /home/osboxes/.pyenv/versions/3.9.5/bin/python -m pdb tests/test_f90_fortran.py
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
    b> /home/osboxes/workspace/foo/tests/test_f90_fortran.py(3)<module>()
    -> """Tests for f90 module `foo.fortran`."""
    (Pdb) b test_f90_add
    Breakpoint 1 at /home/osboxes/workspace/foo/tests/test_f90_fortran.py:14
    (Pdb) r
    [New Thread 0x7ffff3b9a640 (LWP 3824)]
    [New Thread 0x7ffff3399640 (LWP 3825)]
    [New Thread 0x7ffff0b98640 (LWP 3826)]
    [New Thread 0x7fffee397640 (LWP 3827)]
    [New Thread 0x7fffebb96640 (LWP 3828)]
    [New Thread 0x7fffe9395640 (LWP 3829)]
    [New Thread 0x7fffe6b94640 (LWP 3830)]
    [New Thread 0x7fffe4393640 (LWP 3831)]
    [New Thread 0x7fffe1b92640 (LWP 3832)]
    __main__ running <function test_f90_add at 0x7ffff6aaa9d0> ...
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(15)test_f90_add()
    -> x = np.array([0,1,2,3,4],dtype=float)
    (Pdb) n
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(16)test_f90_add()
    -> shape = x.shape
    (Pdb)
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(17)test_f90_add()
    -> y = np.ones (shape,dtype=float)
    (Pdb)
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(18)test_f90_add()
    -> z = np.zeros(shape,dtype=float)
    (Pdb)
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(19)test_f90_add()
    -> expected_z = x + y
    (Pdb)
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(20)test_f90_add()
    -> f90.add(x,y,z)
    (Pdb)
    Thread 1 "python" hit Breakpoint 1, add (x=..., y=..., z=..., n=5) at /home/osboxes/workspace/foo/foo/f90_fortran/fortran.f90:32
    32        do i=1,n
    (gdb) p x
    $1 = (0, 1, 2, 3, 4)
    (gdb) c
    Continuing.
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(21)test_f90_add()
    -> assert (z == expected_z).all()
    (Pdb) c
    -*# finished #*-
    The program finished and will be restarted
    > /home/osboxes/workspace/foo/tests/test_f90_fortran.py(3)<module>()
    -> """Tests for f90 module `foo.fortran`."""
    (Pdb)  

.. note::

   Fortran support in ``Lldb`` seems to be limited. It is possible to step through the
   code, but not the variables are invisible. It is unclear whether this is due to a quirk
   in lldb or f2py on MACOS.

8.2.1. Visual Studio Code
^^^^^^^^^^^^^^^^^^^^^^^^^

Visual_studio_code is an IDE that misfree, open source, and available for Windows,
Linux and MACOS. It supports graphical mixed language debugging for Python, C++ and
Fortran. In addition it is possible to work remotely using ssh (as is eclipse_). You
can edit remote files with Visual Studio's builtin editor, and have a remote terminal
as well. The above debugging approaches can be applied in a remote terminal. So, it is
possible to use it for development on the (VSC) clusters. Here are some useful links;

* `mixed language debugging <https://nadiah.org/2020/03/01/example-debug-mixed-python-c-in-visual-studio-code/>`_

* `Remote Development using SSH <https://code.visualstudio.com/docs/remote/ssh>`_

