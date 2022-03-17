.. include:: ../HYPERLINKS.rst

.. _tutorial-2:

2. A first real project
=======================

Let's start with a simple problem: a Python module that computes the
`scalar product of two arrays <https://en.wikipedia.org/wiki/Dot_product>`_,
generally referred to as the *dot product*. Admittedly, this not a very rewarding
goal, as there are already many Python packages, e.g. Numpy_, that solve this problem
in an elegant and efficient way. However, because the dot product is such a simple
concept in linear algebra, it allows us to illustrate the usefulness of Python as a
language for HPC, as well as the capabilities of Micc2_.

First, we set up a new project for this *dot* project, with the name :file:`ET-dot`,
``ET`` being my initials (check out :ref:`project-and-module-naming`). 

.. code-block:: bash

    > micc2 create ET-dot --remote=none
    [INFO]           [ Creating project directory (ET-dot):
    [INFO]               Python top-level package (et_dot):
    [INFO]               [ Creating local git repository
    [INFO]               ] done.
    [WARNING]            Creation of remote GitHub repository not requested.
    [INFO]           ] done.
    

We ``cd`` into the project directory, so Micc2_ knows is as the current project.

.. code-block:: bash

    > cd ET-dot

Now, open module file :file:`et_dot.py` in your favourite editor and start coding a
dot product method as below. The example code created by Micc2_ can be removed.

.. code-block:: python

    # -*- coding: utf-8 -*-
    """
    Package et_dot
    ==============
    Python module for computing the dot product of two arrays.
    """
    __version__ = "0.0.0"
    
    def dot(a,b):
        """Compute the dot product of *a* and *b*.
    
        :param a: a 1D array.
        :param b: a 1D array of the same length as *a*.
        :returns: the dot product of *a* and *b*.
        :raises: ValueError if ``len(a)!=len(b)``.
        """
        n = len(a)
        if len(b)!=n:
            raise ValueError("dot(a,b) requires len(a)==len(b).")
        result = 0
        for i in range(n):
            result += a[i]*b[i]
        return result

We defined a :py:meth:`dot` method with an informative doc-string that describes
the parameters, the return value and the kind of exceptions it may raise. If you like,
you can add a ``if __name__ == '__main__':`` clause for quick-and-dirty testing or
debugging (see :ref:`modules-and-scripts`). It is a good idea to commit this
implementation to the local git repository:

.. code-block:: bash

    > git commit -a -m 'implemented dot()'
    [main 2fcf5a2] implemented dot()
     1 file changed, 23 insertions(+), 22 deletions(-)
     rewrite et_dot/__init__.py (71%)
    

(If there was a remote GitHub repository, you could also push that commit
``git push``, as to enable your colleagues to acces the code as well.)

We can use the dot method in a script as follows:

.. code-block:: python

    from et_dot import dot
    
    a = [1,2,3]
    b = [4.1,4.2,4.3]
    a_dot_b = dot(a,b)

Or we might execute these lines at the Python prompt:

.. code-block:: pycon

    >>> from et_dot import dot
    >>> a = [1,2,3]
    >>> b = [4.1,4.2,4.3]
    >>> a_dot_b = dot(a,b)
    >>> expected = 1*4.1 + 2*4.2 +3*4.3
    >>> print(f"a_dot_b = {a_dot_b} == {expected}")
    a_dot_b = 25.4 == 25.4
    
.. note::

   This dot product implementation is naive for several reasons:

    * Python is very slow at executing loops, as compared to Fortran or C++.

    * The objects we are passing in are plain Python :py:obj:`list`s. A :py:obj:`list` is a
      very powerfull data structure, with array-like properties, but it is not exactly an
      array. A :py:obj:`list` is in fact an array of pointers to Python objects, and
      therefor list elements can reference anything, not just a numeric value as we would
      expect from an array. With elements being pointers, looping over the array elements
      implies non-contiguous memory access, another source of inefficiency.

    * The dot product is a subject of Linear Algebra. Many excellent libraries have been
      designed for this purpose. Numpy_ should be your starting point because it is well
      integrated with many other Python packages. There is also
      `Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`_, a C++
      template library for linear algebra that is neatly exposed to Python by pybind11_.

    However, starting out with a simple and naive implementation is not a bad idea at all.
    Once it is proven correct, it can serve as reference implementation to validate later
    improvements.

.. _testing-code:

2.1. Testing the code
---------------------

In order to prove that our implementation of the dot product is correct, we write some
tests. Open the file :file:`tests/et_dot/test_et_dot.py`, remove the original
tests put in by micc2_, and add a new one like below:

.. code-block:: python

    import et_dot
    
    def test_dot_aa():
        a = [1,2,3]
        expected = 14
        result = et_dot.dot(a,a)
        assert result==expected

The test :py:meth:`test_dot_aa` defines an array with 3 ``int`` numbers, and
computes the dot product with itself. The expected result is easily calculated by
hand. Save the file, and run the test, usi           ng Pytest_ as explained in
:ref:`testing-your-code`. Pytest_ will show a line for every test source file an on
each such line a ``.`` will appear for every successfull test, and a ``F`` for a failing
test. Here is the result:

.. code-block:: bash

    > pytest tests
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collected 1 item
    
    tests/et_dot/test_et_dot.py .                                            [100%]
    
    ============================== 1 passed in 0.01s ===============================
    

Great, our test succeeds. If you want some more detail you can add the ``-v`` flag.
Pytest_ always captures the output without showing it. If you need to see it to help you
understand errors, add the ``-s`` flag.

We thus have added a single test and verified that it works by running ''pytest''. It is
good practise to commit this to our local git repository:

.. code-block:: bash

    > git commit -a -m 'added test_dot_aa()'
    [main 023191a] added test_dot_aa()
     1 file changed, 9 insertions(+), 36 deletions(-)
     rewrite tests/et_dot/test_et_dot.py (98%)
    

Obviously, our test tests only one particular case, and, perhaps, other cases might
fail. A clever way of testing is to focus on properties. From mathematics we now that
the dot product is commutative. Let's add a test for that. Open
:file:`test_et_dot.py` again and add this code:

.. code-block:: python

    import et_dot
    import random
    
    def test_dot_commutative():
        # create two arrays of length 10 with random float numbers:
        a = []
        b = []
        for _ in range(10):
            a.append(random.random())
            b.append(random.random())
        # test commutativity:
        ab = et_dot.dot(a,b)
        ba = et_dot.dot(b,a)
        assert ab==ba

.. note::

   Focussing on mathematical properties sometimes requires a bit more thought. Our
   mathematical intuition is based on the properties of real numbers - which, as a matter
   of fact, have infinite precision. Programming languages, however, use floating
   point numbers, which have a finite precision. The mathematical properties for
   floating point numbers are not the same as for real numbers. we'll come to that later.

.. code-block:: bash

    > pytest tests -v
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1 -- /Users/etijskens/.pyenv/versions/3.8.5/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collecting ... collected 2 items
    
    tests/test_et_dot.py::test_dot_commutative PASSED                        [ 50%]
    tests/et_dot/test_et_dot.py::test_dot_aa PASSED                          [100%]
    
    ============================== 2 passed in 0.02s ===============================
    

The new test passes as well.

Above we used the :py:meth:`random` module from Python's standard library for
generating the random numbers that populate the array. Every time we run the test,
different random numbers will be generated. That makes the test more powerful and
weaker at the same time. By running the test over and over againg new random arrays will
be tested, growing our cofidence inour dot product implementations. Suppose,
however, that all of a sudden thetest fails. What are we going to do? We know that
something is wrong, but we have no means of investigating the source of the error,
because the next time we run the test the arrays will be different again and the test may
succeed again. The test is irreproducible. Fortunateely, that can be fixed by
setting the seed of the random number generator:

.. code-block:: python

    def test_dot_commutative():
        # Fix the seed for the random number generator of module random.
        random.seed(0)
        # choose array size
        n = 10
        # create two arrays of length 10 with zeroes:
        a = n*[0]
        b = n*[0]
        # repeat the test 1000 times:
        for _ in range(1000):
            for i in range(10):
                 a[i] = random.random()
                 b[i] = random.random()
        # test commutativity:
        ab = et_dot.dot(a,b)
        ba = et_dot.dot(b,a)
        assert ab==ba

.. code-block:: bash

    > pytest tests -v
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1 -- /Users/etijskens/.pyenv/versions/3.8.5/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collecting ... collected 2 items
    
    tests/test_et_dot.py::test_dot_commutative PASSED                        [ 50%]
    tests/et_dot/test_et_dot.py::test_dot_aa PASSED                          [100%]
    
    ============================== 2 passed in 0.03s ===============================
    

The 1000 tests all pass. If, say test 315 would fail, it would fail every time we run it
and the source of error could be investigated.

Another property is that the dot product of an array of ones with another array is the
sum of the elements of the other array. Let us add another test for that:

.. code-block:: python

    def test_dot_one():
        # Fix the seed for the random number generator of module random.
        random.seed(0)
        # choose array size
        n = 10
        # create two arrays of length 10 with zeroes, resp. ones:
        a = n*[0]
        one = n*[1]
        # repeat the test 1000 times:
        for _ in range(1000):
            for i in range(10):
                 a[i] = random.random()
        # test:
        aone = et_dot.dot(a,one)
        expected = sum(a)
        assert aone==expected

.. code-block:: bash

    > pytest tests -v
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1 -- /Users/etijskens/.pyenv/versions/3.8.5/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collecting ... collected 3 items
    
    tests/test_et_dot.py::test_dot_commutative PASSED                        [ 33%]
    tests/test_et_dot.py::test_dot_one PASSED                                [ 66%]
    tests/et_dot/test_et_dot.py::test_dot_aa PASSED                          [100%]
    
    ============================== 3 passed in 0.02s ===============================
    

Success again. We are getting quite confident in the correctness of our
implementation. Here is yet another test:

.. code-block:: python

    def test_dot_one_2():
        a1 = 1.0e16
        a   = [a1 , 1.0, -a1]
        one = [1.0, 1.0, 1.0]
        # test:
        aone = et_dot.dot(a,one)
        expected = 1.0
        assert aone == expected

Clearly, it is a special case of the test above. The expected result is the sum of the
elements in ``a``, that is ``1.0``. Yet it - unexpectedly - fails. Fortunately
pytest_ produces a readable report about the failure:

.. code-block:: bash

    > pytest tests -v
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1 -- /Users/etijskens/.pyenv/versions/3.8.5/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collecting ... collected 4 items
    
    tests/test_et_dot.py::test_dot_commutative PASSED                        [ 25%]
    tests/test_et_dot.py::test_dot_one PASSED                                [ 50%]
    tests/test_et_dot.py::test_dot_one_2 FAILED                              [ 75%]
    tests/et_dot/test_et_dot.py::test_dot_aa PASSED                          [100%]
    
    =================================== FAILURES ===================================
    ________________________________ test_dot_one_2 ________________________________
    
        def test_dot_one_2():
            a1 = 1.0e16
            a   = [a1 , 1.0, -a1]
            one = [1.0, 1.0, 1.0]
            # test:
            aone = et_dot.dot(a,one)
            expected = 1.0
    >       assert aone == expected
    E       assert 0.0 == 1.0
    E         +0.0
    E         -1.0
    
    tests/test_et_dot.py:57: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_et_dot.py::test_dot_one_2 - assert 0.0 == 1.0
    ========================= 1 failed, 3 passed in 0.04s ==========================
    

Mathematically, our expectations about the outcome of the test are certainly
correct. Yet, pytest_ tells us it found that the result is ``0.0`` rather than
``1.0``. What could possibly be wrong? Well our mathematical expectations are based
on our assumption that the elements of ``a`` are real numbers. They aren't. The
elements of ``a`` are floating point numbers, which can only represent a finite
number of decimal digits. *Double precision* numbers, which are the default
floating point type in Python, are typically truncated after 16 decimal digits,
*single precision* numbers after 8. Observe the consequences of this in the Python
statements below:

.. code-block:: pycon

    >>> print( 1.0 + 1e16 )
    1e+16
    >>> print( 1e16 + 1.0 )
    1e+16
    
Because ``1e16`` is a 1 followed by 16 zeroes, adding ``1`` would alter the 17th
digit,which is, because of the finite precision, not represented. An approximate
result is returned, namely ``1e16``, which is of by a relative error of only 1e-16.

.. code-block:: pycon

    >>> print( 1e16 + 1.0 - 1e16 )
    0.0
    >>> print( 1e16 - 1e16 + 1.0 )
    1.0
    >>> print( 1.0 + 1e16 - 1e16 )
    0.0
    
Although each of these expressions should yield ``0.0``, if they were real numbers,
the result differs because of the finite precision. Python executes the expressions
from left to right, so they are equivalent to: 

.. code-block:: pycon

    >>> 1e16 + 1.0 - 1e16 = ( 1e16 + 1.0 ) - 1e16 = 1e16 - 1e16 = 0.0
    >>> 1e16 - 1e16 + 1.0 = ( 1e16 - 1e16 ) + 1.0 = 0.0  + 1.0  = 1.0
    >>> 1.0 + 1e16 - 1e16 = ( 1.0 + 1e16 ) - 1e16 = 1e16 - 1e16 = 0.0

There are several lessons to be learned from this:

* The test does not fail because our code is wrong, but because our mind is used to
  reasoning about real number arithmetic, rather than *floating point arithmetic*
  rules. As the latter is subject to round-off errors, tests sometimes fail
  unexpectedly. Note that for comparing floating point numbers the the standard
  library provides a :py:meth:`math.isclose` method.

* Another silent assumption by which we can be mislead is in the random numbers. In fact,
  :py:meth:`random.random` generates pseudo-random numbers **in the interval
  ``[0,1[``**, which is quite a bit smaller than ``]-inf,+inf[``. No matter how often
  we run the test the special case above that fails will never be encountered, which may
  lead to unwarranted confidence in the code.

So let us fix the failing test using :py:meth:`math.isclose` to account for
round-off errors by specifying an relative tolerance and negating the condition for
the original test:

.. code-block:: python

    def test_dot_one_2():
        a1 = 1.0e16
        a   = [a1 , 1.0, -a1]
        one = [1.0, 1.0, 1.0]
        # test:
        aone = et_dot.dot(a,one)
        expected = 1.0
        assert aone != expected
        assert math.isclose(result, expected, rel_tol=1e-15)

Another aspect that deserves testing the behavior of the code in exceptional
circumstances. Does it indeed raise :py:exc:`ArithmeticError` if the arguments
are not of the same length?

.. code-block:: python

    import pytest
    
    def test_dot_unequal_length():
        a = [1,2]
        b = [1,2,3]
        with pytest.raises(ArithmeticError):
            et_dot.dot(a,b)

Here, :py:meth:`pytest.raises` is a *context manager* that will verify that
:py:exc:`ArithmeticError` is raise when its body is executed. The test will succeed
if indeed the code raises :py:exc:`ArithmeticError` and raise
:py:exc:`AssertionErrorError` if not, causing the test to fail. For an explanation
fo context managers see `The Curious Case of Python's Context Manager
<https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html>`_.Note
that you can easily make :meth:`et_dot.dot` raise other exceptions, e.g.
:exc:`TypeError` by passing in arrays of non-numeric types:

.. code-block:: pycon

    >>> import et_dot
    >>> et_dot.dot([1,2],[1,'two'])
    Traceback (most recent call last):
      File "/Users/etijskens/.local/lib/python3.8/site-packages/et_rstor/__init__.py", line 445, in rstor
        exec(line)
      File "<string>", line 1, in <module>
      File "./et_dot/__init__.py", line 22, in dot
        result += a[i]*b[i]
    TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    
    
Note that it is not the product ``a[i]*b[i]`` for ``i=1`` that is wreaking havoc, but
the addition of its result to ``d``. Furthermore, Don't bother the link to where the
error occured in the traceback. It is due to the fact that this course is completely
generated with Python rather than written by hand).

More tests could be devised, but the current tests give us sufficient confidence. The
point where you stop testing and move on with the next issue, feature, or project is
subject to various considerations, such as confidence, experience, problem
understanding, and time pressure. In any case this is a good point to commit changes
and additions, increase the version number string, and commit the version bumb as
well:

.. code-block:: bash

    > git add tests   #hide#
    
    > git commit -a -m 'dot() tests added'
    [main 1c3b3e7] dot() tests added
     1 file changed, 73 insertions(+)
     create mode 100644 tests/test_et_dot.py
    
    > micc2 version -p
    [INFO]           (ET-dot)> version (0.0.0) -> (0.0.1)
    
    > git commit -a -m 'v0.0.1'
    [main b24f89f] v0.0.1
     2 files changed, 2 insertions(+), 2 deletions(-)
    

The the ``micc2 version`` flag ``-p`` is shorthand for ``--patch``, and requests
incrementing the patch (=last) component of the version string, as seen in the
output. The minor component can be incremented with ``-m`` or ``--minor``, the major
component with ``-M`` or ``--major``. 

At this point you might notice that even for a very simple and well defined function, as
the dot product, the amount of test code easily exceeds the amount of tested code by a
factor of 5 or more. This is not at all uncommon. As the tested code here is an isolated
piece of code, you will probably leave it alone as soon as it passes the tests and you are
confident in the solution. If at some point, the :py:meth:`dot` would failyou should
add a test that reproduces the error and improve the solution so that it passes the
test.

When constructing software for more complex problems, there will be several
interacting components and running the tests after modifying one of the components
will help you assure that all components still play well together, and spot problems
as soon as possible.

.. _improving-efficiency:

2.2. Improving efficiency
-------------------------

There are times when a just a correct solution to the problem at hand issufficient. If
``ET-dot`` is meant to compute a few dot products of small arrays, the naive
implementation above will probably be sufficient. However, if it is to be used many
times and for large arrays and the user is impatiently waiting for the answer, or if
your computing resources are scarse, a more efficient implementation is needed.
Especially in scientific computing and high performance computing, where compute
tasks may run for days using hundreds or even thousands of of compute nodes and
resources are to be shared with many researchers, using the resources efficiently is
of utmost importance and efficient implementations are therefore indispensable.

However important efficiency may be, it is nevertheless a good strategy for
developing a new piece of code, to start out with a simple, even naive implementation,
neglecting efficiency considerations totally, instead focussing on correctness.
Python has a reputation of being an extremely productive programming language. Once
you have proven the correctness of this first version it can serve as a reference
solution to verify the correctness of later more efficient implementations. In
addition, the analysis of this version can highlight the sources of inefficiency and
help you focus your attention to the parts that really need it.

.. _timing-code:

2.2.1. Timing your code
^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to probe the efficiency of your code is to time it: write a simple
script and record how long it takes to execute. Here's a script that computes the dot
product of two long arrays of random numbers.

.. code-block:: python

    """File prof/run1.py"""
    import random
    from et_dot import dot # the dot method is all we need from et_dot
    
    def random_array(n=1000):
        """Create an array with n random numbers in [0,1[."""
        # Below we use a list comprehension (a Python idiom for 
        # creating a list from an iterable object).
        a = [random.random() for i in range(n)]
        return a
    
    if __name__=='__main__':
        a = random_array()
        b = random_array()
        print(dot(a, b))
        print("-*# done #*-")

Executing this script yields:

.. code-block:: bash

    > python ./prof/run1.py
    238.328918524926
    -*# done #*-
    

.. note::

   Every run of this script yields a slightly different outcome because we did not fix
   ``random.seed()``. It will, however, typically be around 250. Since the average
   outcome of ``random.random()`` is 0.5, so every entry contributes on average
   ``0.5*0.5 = 0.25`` and as there are 1000 contributions, that makes on average 250.0.

We are now ready to time our script. There are many ways to achieve this. Here is a
`particularly good introduction <https://realpython.com/python-timer/>`_.
The
`et-stopwatch project <https://et-stopwatch.readthedocs.io/en/latest/readme.html>`_
takes this a little further. It can be installed in your current Python environment
with ``pip``:

.. code-block:: bash

    > python -m pip install et-stopwatch
    Requirement already satisfied: et-stopwatch in /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages (1.0.5)
    

Although ``pip`` is complaining a bit about not being up to date, the installation is
successful.

To time the script above, modify it as below, using the :py:class:`Stopwatch` class
as a context manager:

.. code-block:: python

    """File prof/run1.py"""
    import random
    from et_dot import dot # the dot method is all we need from et_dot
    
    from et_stopwatch import Stopwatch
    
    def random_array(n=1000):
        """Create an array with n random numbers in [0,1[."""
        # Below we use a list comprehension (a Python idiom for 
        # creating a list from an iterable object).
        a = [random.random() for i in range(n)]
        return a
    
    if __name__=='__main__':
        with Stopwatch(message="init"):
            a = random_array()
            b = random_array()
        with Stopwatch(message="dot "):
            a_dot_b = dot(a, b)
        print(a_dot_b)
        print("-*# done #*-")

and execute it again:

.. code-block:: bash

    > python ./prof/run1.py
    init : 0.000262 s
    dot  : 9.4e-05 s
    254.0056419584084
    -*# done #*-
    

When the script is executed each :py:class:`with` block will print the time it takes
to execute its body. The first :py:class:`with` block times the initialisation of
the arrays, and the second times the computation of the dot product. Note that the
initialization of the arrays takes a bit longer than the dot product computation.
Computing random numbers is expensive.

.. _comparison-numpy:

2.2.2. Comparison to Numpy
^^^^^^^^^^^^^^^^^^^^^^^^^^

As said earlier, our implementation of the dot product is rather naive. If you want to
become a good programmer, you should understand that you are probably not the first
researcher in need of a dot product implementation. For most linear algebra
problems, Numpy_ provides very efficient implementations.Below the modified
:file:`run1.py` script adds timing results for the Numpy_ equivalent of our code.

.. code-block:: python

    """File prof/run1.py"""
    # ...
    import numpy as np
    
    if __name__=='__main__':
        with Stopwatch(message="et init"):
            a = random_array()
            b = random_array()
        with Stopwatch(message="et dot "):
            dot(a,b)
        with Stopwatch(message="np init"):
            a = np.random.rand(1000)
            b = np.random.rand(1000)
        with Stopwatch(message="np dot "):
            np.dot(a,b)
        print("-*# done #*-")

Its execution yields:

.. code-block:: bash

    > python ./prof/run1.py
    et init : 0.000282 s
    et dot  : 9.4e-05 s
    np init : 0.000436 s
    np dot  : 8e-06 s
    -*# done #*-
    

Obviously, numpy does significantly better than our naive dot product
implementation. It completes the dot product in 7.5% of the time. It is important to
understand the reasons for this improvement:

* Numpy_ arrays are contiguous data structures of floating point numbers, unlike
  Python's :py:class:`list` which we have been using for our arrays, so far. In a Python
  :py:class:`list` object is in fact a pointer that can point to an arbitrary Python
  object. The items in a Python :py:class:`list` object may even belong to different
  types. Contiguous memory access is far more efficient. In addition, the memory
  footprint of a numpy array is significantly lower that that of a plain Python list.

* The loop over Numpy_ arrays is implemented in a low-level programming languange,
  like C, C++ or Fortran. This allows to make full use of the processors hardware
  features, such as *vectorization* and *fused multiply-add* (FMA).

.. note::

   Note that also the initialisation of the arrays with numpy is almost 6 times faster,
   for roughly the same reasons.

.. _conclusion:

2.2.3. Conclusion
^^^^^^^^^^^^^^^^^

There are three important generic lessons to be learned from this tutorial:

#. Always start your projects with a simple and straightforward implementation which
   can be easily be proven to be correct, even if you know that it will not satisfy your
   efficiency constraints. You should use it as a reference solution to prove the
   correctness of later more efficient implementations.

#. Write test code for proving correctness. Tests must be reproducible, and be run after
   every code extension or modification to ensure that the changes did not break the
   existing code.

#. Time your code to understand which parts are time consuming and which not. Optimize
   bottlenecks first and do not waste time optimizing code that does not contribute
   significantly to the total runtime. Optimized code is typically harder to read and
   may become a maintenance issue.

#. Before you write any code, in this case our dot product implementation, spend some
   time searching the internet to see what is already available. Especially in the field
   of scientific and high performance computing there are many excellent libraries
   available which are hard to beat. Use your precious time for new stuff. Consider
   adding new features to an existing codebase, rather than starting from scratch. It
   will improve your programming skills and gain you time, even though initially your
   progress may seem slower. It might also give your code more visibility, and more
   users, because you provide them with and extra feature on top of something they are
   already used to.

.. _tutorial-3:

3. Binary extension modules
===========================

.. _intro-HPPython:

3.1. Introduction - High Performance Python
-------------------------------------------

Suppose for a moment that our dot product implementation :py:meth:`et_dot.dot()`
we developed in tutorial-2` is way too slow to be practical for the research project
that needs it, and that we did not have access to fast dot product implementations,
such as :py:meth:`numpy.dot()`. The major advantage we took from Python is that
coding :py:meth:`et_dot.dot()` was extremely easy, and even coding the tests
wasn't too difficult. In this tutorial you are about to discover that coding a highly
efficient replacement for :py:meth:`et_dot.dot()` is not too difficult either.
There are several approaches for this. Here are a number of highly recommended links
covering them:

* `Why you should use Python for scientific research <https://developer.ibm.com/dwblog/2018/use-python-for-scientific-research/>`_

* `Performance Python: Seven Strategies for Optimizing Your Numerical Code <https://www.youtube.com/watch?v=zQeYx87mfyw>`_

* `High performance Python 1 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-1>`_

* `High performance Python 2 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-2>`_

* `High performance Python 3 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-3>`_

* `High performance Python 4 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-4>`_

Two of the approaches discussed in the *High Performance Python* series involve
rewriting your code in Modern Fortran or C++ and generate a shared library that can be
imported in Python just as any Python module. This is exactly the approach taken in
important HPC Python modules, such as Numpy_, pyTorch_ and pandas_.Such shared
libraries are called *binary extension modules*. Constructing binary extension
modules is by far the most scalable and flexible of all current acceleration
strategies, as these languages are designed to squeeze the maximum of performance
out of a CPU.

However, figuring out how to build such binary extension modules is a bit of a
challenge, especially in the case of C++. This is in fact one of the main reasons why
Micc2_ was designed: facilitating the construction of binary extension modules and
enabling the developer to create high performance tools with ease. To that end,
Micc2_ can provide boilerplate code for binary extensions as well a practical
wrapper for building the binary extension modules, the ``micc2 build`` command.
This command uses CMake_ to pass the build options to the compiler, while bridging the
gap between C++ and Fortran, on one hand and Python on the other hand using pybind11_
and f2py_. respectively. This is illustrated in the figure below:

.. image:: ../tutorials/im-building.png

There is a difference in how f2py_ and pybind11_ operate. F2py_ is an *executable*
that inspects the Fortran source code and creates wrappers for the subprograms it
finds. These wrappers are C code, compiled and linked with the compiled Fortran code
to build the extension module. Thus, f2py_ needs a Fortran compiler, as well as a C
compiler. The Pybind11_ approach is conceptually simpler. Pybind11_is a
*C++ template library* that the programmer uses to express the interface between
Python and C++. In fact the introspection is done by the programmer, and there is only
one compiler round, using a C++ compiler. This gives the programmer more flexibility
and control, but also a bit more work.

.. _f90-or-cpp:

3.1.1. Choosing between Fortran and C++ for binary extension modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here are a number of arguments that you may wish to take into account for choosing the
programming language for your binary extension modules:

* Fortran is a simpler language than C++.

* It is easier to write efficient code in Fortran than C++.

* C++ is a general purpose language (as is Python), whereas Fortran is meant for
  scientific computing. Consequently, C++ is a much more expressive language.

* C++ comes with a huge standard library, providing lots of data structures and
  algorithms that are hard to match in Fortran. If the standard library is not enough,
  there are also the highly recommended `Boost <https://boost.org>`_ libraries and
  many other high quality domain specific libraries. There are also domain specific
  libraries in Fortran, but their count differs by an order of magnitude at least.

* With Pybind11_ you can almost expose anything from the C++ side to Python, and vice
  versa, not just functions.

* Modern Fortran is (imho) not as good documented as C++. Useful places to look for
  language features and idioms are:

    * Fortran: https://www.fortran90.org/

    * C++: http://www.cplusplus.com/

    * C++: https://en.cppreference.com/w/

In short, C++ provides much more possibilities, but it is not for the novice. As to my
own experience, I discovered that working on projects of moderate complexity I
progressed significantly faster using Fortran rather than C++, despite the fact
that my knowledge of Fortran is quite limited compared to C++. However, your mileage
may vary.

.. _add-bin-ext:

3.2. Adding Binary extensions to a Micc2_ project
-------------------------------------------------

Adding a binary extension to your current project is simple. To add a binary extension
'foo' written in (Modern) Fortran, run:

.. code-block:: bash

    > micc add foo --f90

and for a C++ binary extension, run:

.. code-block:: bash

    > micc add bar --cpp

The ``add`` subcommand adds a component to your project. It specifies a name, here,
``foo``, and a flag to specify the kind of the component, ``--f90`` for a Fortran
binary extension module, ``--cpp`` for a C++ binary extension module. Other
components are a Python sub-module with module structure (``--module``), or
package structure ``--package``, and a CLI script (`--cli` and `--clisub`). 

You can add as many components to your project as you want. 

The binary modules are build with the ``micc2 build`` command. :

.. code-block:: bash

    > micc2 build foo

This builds the Fortran binary extension :file:`foo`. To build all binary
extensions at once, just issue ``micc2 build``.

As Micc2_ always creates complete working examples you can build the binary
extensions right away and run their tests with pytest_

If there are no syntax errors the binary extensions will be built, and you will be able
to import the modules :py:mod:`foo` and :py:mod:`bar` in your project scripts and
use their subroutines and functions. Because :py:mod:`foo` and :py:mod:`bar` are
submodules of your micc_ project, you must import them as:

.. code-block:: 

    import my_package.foo
    import my_package.bar
    
    # call foofun in my_package.foo
    my_package.foo.foofun(...)
    
    # call barfun in my_package.bar
    my_package.bar.barfun(...)

.. _micc2-build-options:

3.2.1. Build options
^^^^^^^^^^^^^^^^^^^^

Here is an overview of ``micc2 build`` options:

.. code-block:: bash

    > micc2 build --help
    Usage: micc2 build [OPTIONS] [MODULE]
    
      Build binary extensions.
    
      :param str module: build a binary extension module. If not specified or
      all binary     extension modules are built.
    
    Options:
      -b, --build-type TEXT  build type: any of the standard CMake build types:
                             Release (default), Debug, RelWithDebInfo, MinSizeRel.
      --clean                Perform a clean build, removes the build directory
                             before the build, if there is one. Note that this
                             option is necessary if the extension's
                             ``CMakeLists.txt`` was modified.
      --cleanup              Cleanup remove the build directory after a successful
                             build.
      --help                 Show this message and exit.
    

.. _building-f90:

3.3. Building binary extension modules from Fortran
---------------------------------------------------

So, in order to implement a more efficient dot product, let us add a Fortran binary
extension module with name ``dotf``:

.. code-block:: bash

    > micc2 add dotf --f90
    [INFO]           [ Adding f90 submodule dotf to package et_dot.
    [INFO]               - Fortran source in       /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.f90.
    [INFO]               - build settings in       /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/CMakeLists.txt.
    [INFO]               - module documentation in /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.rst (restructuredText format).
    [INFO]               - Python test code in     /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/tests/et_dot/dotf/test_dotf.py.
    [INFO]           ] done.
    

The command now runs successfully, and the output tells us where to enter the Fortran
source code, the build settings, the test code and the documentation of the added
module. Everything related to the :file:`dotf` sub-module is in subdirectory
:file:`ET-dot/et_dot/dotf`. That directory has a ``f90_`` prefix indicating that
it relates to a Fortran binary extension module. As useal, these files contain
already working example code that you an inspect to learn how things work.

Let's continue our development of a Fortran version of the dot product. Open file
:file:`ET-dot/et_dot/dotf/dotf.f90` in your favorite editor or IDE and replace
the existing example code in the Fortran source file with:

.. code-block:: fortran

    function dot(a,b,n)
      ! Compute the dot product of a and b
        implicit none
        real*8 :: dot ! return  value
      !-----------------------------------------------
      ! Declare function parameters
        integer*4              , intent(in)    :: n
        real*8   , dimension(n), intent(in)    :: a,b
      !-----------------------------------------------
      ! Declare local variables
        integer*4 :: i
      !-----------------------------------------------'
        dot = 0.
        do i=1,n
            dot = dot + a(i) * b(i)
        end do
    end function dot

The binary extension module can now be built:

.. code-block:: bash

    > micc2 build dotf
    [INFO] [ Building f90 module 'et_dot/dotf':
    [DEBUG]          [ > cmake -D PYTHON_EXECUTABLE=/Users/etijskens/.pyenv/versions/3.8.5/bin/python ..
    [DEBUG]              (stdout)
                           -- The Fortran compiler identification is GNU 11.2.0
                           -- Checking whether Fortran compiler has -isysroot
                           -- Checking whether Fortran compiler has -isysroot - yes
                           -- Checking whether Fortran compiler supports OSX deployment target flag
                           -- Checking whether Fortran compiler supports OSX deployment target flag - yes
                           -- Detecting Fortran compiler ABI info
                           -- Detecting Fortran compiler ABI info - done
                           -- Check for working Fortran compiler: /usr/local/bin/gfortran - skipped
                           -- Checking whether /usr/local/bin/gfortran supports Fortran 90
                           -- Checking whether /usr/local/bin/gfortran supports Fortran 90 - yes
                           
                           # Build settings ###################################################################################
                           CMAKE_Fortran_COMPILER: /usr/local/bin/gfortran
                           CMAKE_BUILD_TYPE      : Release
                           F2PY_opt              : --opt='-O3'
                           F2PY_arch             : 
                           F2PY_f90flags         : 
                           F2PY_debug            : 
                           F2PY_defines          : -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION;-DF2PY_REPORT_ON_ARRAY_COPY=1;-DNDEBUG
                           F2PY_includes         : 
                           F2PY_linkdirs         : 
                           F2PY_linklibs         : 
                           module name           : dotf.cpython-38-darwin.so
                           module filepath       : /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/dotf.cpython-38-darwin.so
                           source                : /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.f90
                           python executable     : /Users/etijskens/.pyenv/versions/3.8.5/bin/python [version=Python 3.8.5]
                             f2py executable     : /Users/etijskens/.pyenv/versions/3.8.5/bin/f2py [version=2]
                           ####################################################################################################
                           -- Configuring done
                           -- Generating done
                           -- Build files have been written to: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build
    [DEBUG]          ] done.
    [DEBUG]          [ > make VERBOSE=1
    [DEBUG]              (stdout)
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -S/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf -B/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build --check-build-system CMakeFiles/Makefile.cmake 0
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_progress_start /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/CMakeFiles /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build//CMakeFiles/progress.marks
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/Makefile2 all
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/dotf.dir/build.make CMakeFiles/dotf.dir/depend
                           cd /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build && /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_depends "Unix Makefiles" /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/CMakeFiles/dotf.dir/DependInfo.cmake --color=
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/dotf.dir/build.make CMakeFiles/dotf.dir/build
                           [100%] Generating dotf.cpython-38-darwin.so
                           /Users/etijskens/.pyenv/versions/3.8.5/bin/f2py -m dotf -c --f90exec=/usr/local/bin/gfortran /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.f90 -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION -DF2PY_REPORT_ON_ARRAY_COPY=1 -DNDEBUG --opt='-O3' --build-dir /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build
                           running build
                           running config_cc
                           unifing config_cc, config, build_clib, build_ext, build commands --compiler options
                           running config_fc
                           unifing config_fc, config, build_clib, build_ext, build commands --fcompiler options
                           running build_src
                           build_src
                           building extension "dotf" sources
                           f2py options: []
                           f2py:> /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotfmodule.c
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8
                           Reading fortran codes...
                           	Reading file '/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.f90' (format:free)
                           Post-processing...
                           	Block: dotf
                           			Block: dot
                           Post-processing (stage 2)...
                           Building modules...
                           	Building module "dotf"...
                           		Creating wrapper for Fortran function "dot"("dot")...
                           		Constructing wrapper function "dot"...
                           		  dot = dot(a,b,[n])
                           	Wrote C/API module "dotf" to file "/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotfmodule.c"
                           	Fortran 77 wrappers are saved to "/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotf-f2pywrappers.f"
                             adding '/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/fortranobject.c' to sources.
                             adding '/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8' to include_dirs.
                           copying /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/numpy/f2py/src/fortranobject.c -> /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8
                           copying /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/numpy/f2py/src/fortranobject.h -> /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8
                             adding '/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotf-f2pywrappers.f' to sources.
                           build_src: building npy-pkg config files
                           running build_ext
                           customize UnixCCompiler
                           customize UnixCCompiler using build_ext
                           get_default_fcompiler: matching types: '['gnu95', 'nag', 'absoft', 'ibm', 'intel', 'gnu', 'g95', 'pg']'
                           customize Gnu95FCompiler
                           Found executable /usr/local/bin/gfortran
                           Found executable /usr/local/bin/gfortran
                           customize Gnu95FCompiler
                           customize Gnu95FCompiler using build_ext
                           building 'dotf' extension
                           compiling C sources
                           C compiler: clang -Wno-unused-result -Wsign-compare -Wunreachable-code -DNDEBUG -g -fwrapv -O3 -Wall -I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include -I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include
                           
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build
                           creating /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8
                           compile options: '-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION -DF2PY_REPORT_ON_ARRAY_COPY=1 -DNDEBUG -DNPY_DISABLE_OPTIMIZATION=1 -I/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8 -I/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/numpy/core/include -I/Users/etijskens/.pyenv/versions/3.8.5/include/python3.8 -c'
                           clang: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotfmodule.c
                           clang: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/fortranobject.c
                           /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotfmodule.c:144:12: warning: unused function 'f2py_size' [-Wunused-function]
                           static int f2py_size(PyArrayObject* var, ...)
                                      ^
                           1 warning generated.
                           compiling Fortran sources
                           Fortran f77 compiler: /usr/local/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -fPIC -O3
                           Fortran f90 compiler: /usr/local/bin/gfortran -Wall -g -fno-second-underscore -fPIC -O3
                           Fortran fix compiler: /usr/local/bin/gfortran -Wall -g -ffixed-form -fno-second-underscore -Wall -g -fno-second-underscore -fPIC -O3
                           compile options: '-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION -DF2PY_REPORT_ON_ARRAY_COPY=1 -DNDEBUG -I/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8 -I/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/numpy/core/include -I/Users/etijskens/.pyenv/versions/3.8.5/include/python3.8 -c'
                           gfortran:f90: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.f90
                           gfortran:f77: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotf-f2pywrappers.f
                           /usr/local/bin/gfortran -Wall -g -Wall -g -undefined dynamic_lookup -bundle /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotfmodule.o /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/fortranobject.o /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/dotf.o /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/src.macosx-10.15-x86_64-3.8/dotf-f2pywrappers.o -L/usr/local/Cellar/gcc/11.2.0/lib/gcc/11/gcc/x86_64-apple-darwin20/11.2.0 -L/usr/local/Cellar/gcc/11.2.0/lib/gcc/11/gcc/x86_64-apple-darwin20/11.2.0/../../.. -L/usr/local/Cellar/gcc/11.2.0/lib/gcc/11/gcc/x86_64-apple-darwin20/11.2.0/../../.. -lgfortran -o ./dotf.cpython-38-darwin.so
                           ld: warning: dylib (/usr/local/Cellar/gcc/11.2.0/lib/gcc/11/libgfortran.dylib) was built for newer macOS version (11.3) than being linked (10.15)
                           ld: warning: dylib (/usr/local/Cellar/gcc/11.2.0/lib/gcc/11/libquadmath.dylib) was built for newer macOS version (11.3) than being linked (10.15)
                           [100%] Built target dotf
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_progress_start /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/_cmake_build/CMakeFiles 0
    [DEBUG]          ] done.
    [DEBUG]          [ > make install
    [DEBUG]              (stdout)
                           [100%] Built target dotf
                           Install the project...
                           -- Install configuration: "Release"
                           -- Installing: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf/../dotf.cpython-38-darwin.so
    [DEBUG]          ] done.
    [INFO] ] done.
    [INFO]           Binary extensions built successfully:
    [INFO]           - /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotf.cpython-38-darwin.so
    

The command produces a lot of output, which comes from CMake, f2py, thecompilation of
the Fortran code, and the compilation of the wrappers of the fortran code, which are
written in C.If there are no syntax errors in the Fortran code, the binary extension
module will build successfully, as above and be installed in a the package directory
of our project :file:`ET-dot/et_dot`. The full module name is
:file:`dotf.cpython-38-darwin.so`. The extension is composed of: the kind of
Python distribution (``cpython``), the MAJORminor version string of the Python
version being used (``38`` as we are running Python 3.8.5), the OS on which we are
working (``<module 'os' from
'/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/os.py'>``), and an
extension indicating a shared library on this OS (``.so``). This file can be imported
in a Python script, by using the filename without the extension, i.e. ``dotf``. As the
module was built successfully, we can test it. Here is some test code. Enter it in file
:file:`ET-dot/tests/test_dotf.py`:

.. code-block:: Python

    import numpy as np
    import et_dot
    # create an alias for the dotf binary extension module
    f90 = et_dot.dotf
    
    def test_dot_aa():
        # create an numpy array of floats:
        a = np.array([0,1,2,3,4],dtype=float)
        # use the original dot implementation to compute the expected result:
        expected = et_dot.dot(a,a)
        # call the dot function in the binary extension module with the same arguments:
        a_dot_a = f90.dot(a,a)
        assert a_dot_a == expected

Then run the test (we only run the test for the dotf module, as we did not touch the
:py:meth:`et_dot.dot` implementation):

.. code-block:: bash

    > pytest tests/et_dot/dotf/test_dotf.py
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collected 1 item
    
    tests/et_dot/dotf/test_dotf.py .                                         [100%]
    
    ============================== 1 passed in 0.42s ===============================
    

The astute reader will notice the magic that is happening here: ``a`` is a numpy array,
which is passed as the first and second parameter to the :py:meth:`et_dot.dotf.dot`
function defined in our binary extension module. Note that the third parameter of the
:py:meth:`et_dot.dotf.dot` function is omitted. How did that happen? The
``micc2 build`` command uses f2py_ to build the binary extension module. When
calling :py:meth:`et_dot.dotf.dot` you are in fact calling a wrapper function that
f2py created that extracts the pointer to the memory of array ``a`` and its length. The
wrapper function then calls the Fortran function with the approprioate parameters
as specified in the Fortran function definition. This invisible wrapper function is
in fact rather intelligent, it even handles type conversions. E.g. we can pass in a
Python array, and the wrapper will convert it into a numpy array, or an array of ints,
and the wrapper will convert it into a float array. In fact the wrapper considers all
implicit type conversions allowed by Python. However practical this feature may be,
type conversion requires copying the entire array and converting each element. For
long arrays this may be prohibitively expensive. For this reason the
:file:`et_dot/dotf/CMakeLists.txt` file specifies the
``F2PY_REPORT_ON_ARRAY_COPY=1`` flag which makes the wrappers issue a warning to
tell you that you should modify the client program to pass types to the wrapper which to
not require conversion.

.. code-block:: pycon

    >>> import et_dot
    >>> a = [1,2,3]
    >>> b = [2,2,2]
    >>> print(et_dot.dot(a,b))
    12
    >>> print(et_dot.dotf.dot(a,b))
    12.0
    created an array from object
    created an array from object
    
Here, ``a`` and ``b`` are plain Python lists, not numpy arrays, andthey contain
``int`` numbers. :py:meth:`et_dot.dot()` therefore also returns an int (``12``).
However, the Fortran implementation :py:meth:`et_dot.dotf.dot()` expects an
array of floats and returns a float (``12.0``). The wrapper converts the Python lists
``a`` and ``b`` to numpy ``float`` arrays. If the binary extension module was
compiled with
``F2PY_REPORT_ON_ARRAY_COPY=1`` (the default setting) the wrapper will warn you with the message``created an array from object``.
If we construct the numpy arrays ourselves, but still of type ``int``, the wrapper has
to convert the ``int`` array into a ``float`` array, because that is what corresponds
the the Fortran ``real*8`` type, and will warn that it *copied* the array to make the
conversion:

.. code-block:: pycon

    >>> import et_dot
    >>> import numpy as np
    >>> a = np.array([1,2,3])
    >>> b = np.array([2,2,2])
    >>> print(et_dot.dot(a,b))
    12
    >>> print(et_dot.dotf.dot(a,b))
    12.0
    copied an array: size=3, elsize=8
    copied an array: size=3, elsize=8
    
Here, ``size`` refers to the length of the array, and elsize is thenumber of bytes
needed for each element of the target array type, c.q. a ``float``.

.. note::

   The wrappers themselves are generated in C code, so, you not only need a Fortran
   compiler, but also a C compiler.

Note that the test code did not explicitly import :py:mod:`et_dot.dotf`, just
:py:mod:`et_dot`. This is only possible because Micc2 has modified
:file:`et_dot/__init__.py` to import every submodule that has been added to the
project:

.. code-block:: python

    # in file et_dot/__init__.py
    import et_dot.dotf

If the submodule :py:mod:`et_dot.dotf` was not built or failed to build, that import
statement will fail and raise a :py:exc:`ModuleNotFoundError` exception. Micc2
has added a little extra magic to attempt to build the module automatically in that
case:

.. code-block:: python

    # in file et_dot/__init__.py
    try:
        import et_dot.dotf
    except ModuleNotFoundError as e:
        # Try to build this binary extension:
        from pathlib import Path
        import click
        from et_micc2.project import auto_build_binary_extension
        msg = auto_build_binary_extension(Path(__file__).parent, "dotf")
        if not msg:
            import et_dot.dotf
        else:
            click.secho(msg, fg="bright_red")

Obviously, you should also add the other tests we created for the Python
implementation. 

