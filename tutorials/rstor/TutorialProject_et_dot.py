import json
import sys

from helpers import *
from et_rstor import *

project_name = 'ET-dot'
project_path = workspace / project_name



def TutorialProject_et_dot_1():
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    doc = RstDocument('TutorialProject_et_dot_1', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading('A first real project', level=2, crosslink='tutorial-2')

    Paragraph(
        "Let's start with a simple problem: a Python module that computes the "
        "`scalar product of two arrays <https://en.wikipedia.org/wiki/Dot_product>`_, "
        "generally referred to as the *dot product*. Admittedly, this not a very "
        "rewarding goal, as there are already many Python packages, e.g. Numpy_, "
        "that solve this problem in an elegant and efficient way. However, because "
        "the dot product is such a simple concept in linear algebra, it allows us to "
        "illustrate the usefulness of Python as a language for HPC, as well as the "
        "capabilities of Micc2_."
    )
    Paragraph(
        "First, we set up a new project for this *dot* project, with the name "
        ":file:`ET-dot`, ``ET`` being my initials (check out :ref:`project-and-module-naming`). "
        # "Not knowing beforehand how involved this project will become, "
        # "we create a simple *module* project without a remote Github_ repository:"
    )
    CodeBlock(
        f'micc2 create {project_name} --package --remote=none'
        , language='bash', execute=True, cwd=workspace
    )
    # --------------------------------------------------------------------------------
    # We want to be able use the packagee we create in this tutorial. Apparently,
    # Python cannot reload the module correctly after it changes its structure from
    # module to package. So, this is the true reason why we need to create a
    # package from the beginning: otherwise we would not be able to execute the
    # et_dot's code inside the tutorial.
    # --------------------------------------------------------------------------------
    Paragraph(
        "We already create a package project, rather than the default module project, "
        "just to avoid having to ``micc2 convert-to-package`` later, and to be prepared "
        "for having to add other components (See the :ref:`modules-and-packages` section"
        "for details on the difference between projects with a module structure and a "
        "package structure)."
    )
    Paragraph(
        "We ``cd`` into the project directory, so Micc2_ knows is as the current project."
    )
    CodeBlock(
        'cd ET-dot'
        , language='bash'
    )
    Paragraph(
        "Now, open module file :file:`et_dot.py` in your favourite editor and start coding "
        "a dot product method as below. The example code created by Micc2_ can be removed."
    )
    CodeBlock(
        ['# -*- coding: utf-8 -*-'
            , '"""'
            , 'Package et_dot'
            , '=============='
            , 'Python module for computing the dot product of two arrays.'
            , '"""'
            , '__version__ = "0.0.0"'
            , ''
            , 'def dot(a,b):'
            , '    """Compute the dot product of *a* and *b*.'
            , ''
            , '    :param a: a 1D array.'
            , '    :param b: a 1D array of the same length as *a*.'
            , '    :returns: the dot product of *a* and *b*.'
            , '    :raises: ValueError if ``len(a)!=len(b)``.'
            , '    """'
            , '    n = len(a)'
            , '    if len(b)!=n:'
            , '        raise ValueError("dot(a,b) requires len(a)==len(b).")'
            , '    result = 0'
            , '    for i in range(n):'
            , '        result += a[i]*b[i]'
            , '    return result'
         ]
        , language='python', copyto=project_path / 'et_dot/__init__.py'
    )
    Paragraph(
        "We defined a :py:meth:`dot` method with an informative doc-string that describes "
        "the parameters, the return value and the kind of exceptions it may raise. If "
        "you like, you can add a ``if __name__ == '__main__':`` clause for quick-and-dirty "
        "testing or debugging (see :ref:`modules-and-scripts`). It is a good idea to commit "
        "this implementation to the local git repository:"
    )
    CodeBlock(
        "git commit -a -m 'implemented dot()'"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "(If there was a remote GitHub repository, you could also push that commit ``git push``, "
        "as to enable your colleagues to acces the code as well.)"
    )
    Paragraph(
        "We can use the dot method in a script as follows:"
    )
    CodeBlock(
        ['from et_dot import dot'
            , ''
            , 'a = [1,2,3]'
            , 'b = [4.1,4.2,4.3]'
            , 'a_dot_b = dot(a,b)'
         ]
        , language='python'
    )
    Paragraph(
        'Or we might execute these lines at the Python prompt:'
    )
    CodeBlock(
        ['from et_dot import dot'
            , 'a = [1,2,3]'
            , 'b = [4.1,4.2,4.3]'
            , 'a_dot_b = dot(a,b)'
            , 'expected = 1*4.1 + 2*4.2 +3*4.3'
            , 'print(f"a_dot_b = {a_dot_b} == {expected}")'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    Note(
        'This dot product implementation is naive for several reasons:'
    )
    List(
        ['Python is very slow at executing loops, as compared to Fortran or C++.'
            , 'The objects we are passing in are plain Python :py:obj:`list`s. A :py:obj:`list` '
              'is a very powerfull data structure, with array-like properties, but it is not '
              'exactly an array. A :py:obj:`list` is in fact an array of pointers to Python '
              'objects, and therefor list elements can reference anything, not just a numeric '
              'value as we would expect from an array. With elements being pointers, looping '
              'over the array elements implies non-contiguous memory access, another source of '
              'inefficiency.'
            , 'The dot product is a subject of Linear Algebra. Many excellent libraries have been '
              'designed for this purpose. Numpy_ should be your starting point because it is well '
              'integrated with many other Python packages. There is also '
              '`Eigen <http://eigen.tuxfamily.org/index.php?title=Main_Page>`_, a C++ template '
              'library for linear algebra that is neatly exposed to Python by pybind11_.'
         ]
        , indent=4
    )
    Paragraph(
        'However, starting out with a simple and naive implementation is not a bad idea at all. '
        'Once it is proven correct, it can serve as reference implementation to validate later '
        'improvements.'
        , indent=4
    )

    Heading('Testing the code', level=3, crosslink='testing-code')

    Paragraph(
        "In order to prove that our implementation of the dot product is correct, we write "
        "some tests. Open the file :file:`tests/test_et_dot.py`, remove the original "
        "tests put in by micc2_, and add a new one like below:"
    )
    CodeBlock(
        ['import et_dot'
            , ''
            , 'def test_dot_aa():'
            , '    a = [1,2,3]'
            , '    expected = 14'
            , '    result = et_dot.dot(a,a)'
            , '    assert result==expected'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py'
    )
    Paragraph(
        'The test :py:meth:`test_dot_aa` defines an array with 3 ``int`` '
        'numbers, and computes the dot product with itself. The expected '
        'result is easily calculated by hand. '
        'Save the file, and run the test, usi           ng Pytest_ as explained in '
        ':ref:`testing-your-code`. Pytest_ will show a line for every test '
        'source file an on each such line a ``.`` will appear for every '
        'successfull test, and a ``F`` for a failing test. Here is the '
        'result:'
    )
    CodeBlock(
        "pytest tests"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        'Great, our test succeeds. If you want some more detail you can add the '
        '``-v`` flag. Pytest_ always captures the output without showing it. '
        'If you need to see it to help you understand errors, add the ``-s`` flag.'
    )
    Paragraph(
        "We thus have added a single test and verified that it works by running "
        "''pytest''. It is good practise to commit this to our local git repository:"
    )
    CodeBlock(
        "git commit -a -m 'added test_dot_aa()'"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "Obviously, our test tests only one particular case, and, perhaps, other "
        "cases might fail. A clever way of testing is to focus on properties. "
        "From mathematics we now that the dot product is commutative. Let's add a "
        "test for that. Open :file:`test_et_dot.py` again and add this code:"
    )
    CodeBlock(
        ['import random'
            , ''
            , 'def test_dot_commutative():'
            , '    # create two arrays of length 10 with random float numbers:'
            , '    a = []'
            , '    b = []'
            , '    for _ in range(10):'
            , '        a.append(random.random())'
            , '        b.append(random.random())'
            , '    # test commutativity:'
            , '    ab = et_dot.dot(a,b)'
            , '    ba = et_dot.dot(b,a)'
            , '    assert ab==ba'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    Note(
        "Focussing on mathematical properties sometimes requires a bit more thought. "
        "Our mathematical intuition is based on the properties of real numbers - which, "
        "as a matter of fact, have infinite precision. Programming languages, however, "
        "use floating point numbers, which have a finite precision. The mathematical "
        "properties for floating point numbers are not the same as for real numbers. "
        "we'll come to that later."
    )
    CodeBlock(
        "pytest tests -v"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "The new test passes as well."
    )
    Paragraph(
        "Above we used the :py:meth:`random` module from Python's standard library "
        "for generating the random numbers that populate the array. Every time we "
        "run the test, different random numbers will be generated. That makes the "
        "test more powerful and weaker at the same time. By running the test over "
        "and over againg new random arrays will be tested, growing our cofidence in"
        "our dot product implementations. Suppose, however, that all of a sudden the"
        "test fails. What are we going to do? We know that something is wrong, but "
        "we have no means of investigating the source of the error, because the next "
        "time we run the test the arrays will be different again and the test may "
        "succeed again. The test is irreproducible. Fortunateely, that can be fixed "
        "by setting the seed of the random number generator:"
    )
    CodeBlock(
        ['def test_dot_commutative():'
            , '    # Fix the seed for the random number generator of module random.'
            , '    random.seed(0)'
            , '    # choose array size'
            , '    n = 10'
            , '    # create two arrays of length 10 with zeroes:'
            , '    a = n*[0]'
            , '    b = n*[0]'
            , '    # repeat the test 1000 times:'
            , '    for _ in range(1000):'
            , '        for i in range(10):'
            , '             a[i] = random.random()'
            , '             b[i] = random.random()'
            , '    # test commutativity:'
            , '    ab = et_dot.dot(a,b)'
            , '    ba = et_dot.dot(b,a)'
            , '    assert ab==ba'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    CodeBlock(
        "pytest tests -v"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "The 1000 tests all pass. If, say test 315 would fail, it would fail every time "
        "we run it and the source of error could be investigated."
    )
    Paragraph(
        "Another property is that the dot product of an array of ones with another array "
        "is the sum of the elements of the other array. Let us add another test for that:"
    )
    CodeBlock(
        ['def test_dot_one():'
            , '    # Fix the seed for the random number generator of module random.'
            , '    random.seed(0)'
            , '    # choose array size'
            , '    n = 10'
            , '    # create two arrays of length 10 with zeroes, resp. ones:'
            , '    a = n*[0]'
            , '    one = n*[1]'
            , '    # repeat the test 1000 times:'
            , '    for _ in range(1000):'
            , '        for i in range(10):'
            , '             a[i] = random.random()'
            , '    # test:'
            , '    aone = et_dot.dot(a,one)'
            , '    expected = sum(a)'
            , '    assert aone==expected'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    CodeBlock(
        "pytest tests -v"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "Success again. We are getting quite confident in the correctness of our implementation. "
        "Here is yet another test:"
    )
    CodeBlock(
        ['def test_dot_one_2():'
            , '    a1 = 1.0e16'
            , '    a   = [a1 , 1.0, -a1]'
            , '    one = [1.0, 1.0, 1.0]'
            , '    # test:'
            , '    aone = et_dot.dot(a,one)'
            , '    expected = 1.0'
            , '    assert aone == expected'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    Paragraph(
        "Clearly, it is a special case of the test above. The expected result is the sum "
        "of the elements in ``a``, that is ``1.0``. Yet it - unexpectedly - fails. "
        "Fortunately pytest_ produces a readable report about the failure:"
    )
    CodeBlock(
        "pytest tests -v"
        , language='bash', execute=True, cwd=project_path, error_ok=True
    )
    Paragraph(
        "Mathematically, our expectations about the outcome of the test are certainly correct. "
        "Yet, pytest_ tells us it found that the result is ``0.0`` rather than ``1.0``. What "
        "could possibly be wrong? Well our mathematical expectations are based on our assumption "
        "that the elements of ``a`` are real numbers. They aren't. The elements of ``a`` are "
        "floating point numbers, which can only represent a finite number of decimal digits. "
        "*Double precision* numbers, which are the default floating point type in Python, are "
        "typically truncated after 16 decimal digits, *single precision* numbers after 8. "
        "Observe the consequences of this in the Python statements below:"
    )
    CodeBlock(
        ["print( 1.0 + 1e16 )"
            , "print( 1e16 + 1.0 )"
         ]
        , language='pycon', execute=True
    )
    Paragraph(
        "Because ``1e16`` is a 1 followed by 16 zeroes, adding ``1`` would alter the 17th digit,"
        "which is, because of the finite precision, not represented. An approximate result is "
        "returned, namely ``1e16``, which is of by a relative error of only 1e-16."
    )
    CodeBlock(
        ["print( 1e16 + 1.0 - 1e16 )"
            , "print( 1e16 - 1e16 + 1.0 )"
            , "print( 1.0 + 1e16 - 1e16 )"
         ]
        , language='pycon', execute=True
    )
    Paragraph(
        "Although each of these expressions should yield ``0.0``, if they were real numbers, "
        "the result differs because of the finite precision. Python executes the expressions "
        "from left to right, so they are equivalent to: "
    )
    CodeBlock(
        ["1e16 + 1.0 - 1e16 = ( 1e16 + 1.0 ) - 1e16 = 1e16 - 1e16 = 0.0"
            , "1e16 - 1e16 + 1.0 = ( 1e16 - 1e16 ) + 1.0 = 0.0  + 1.0  = 1.0"
            , "1.0 + 1e16 - 1e16 = ( 1.0 + 1e16 ) - 1e16 = 1e16 - 1e16 = 0.0"
         ]
        , language='pycon'
    )
    Paragraph(
        "There are several lessons to be learned from this:"
    )
    List(
        ["The test does not fail because our code is wrong, but because our mind is used to "
         "reasoning about real number arithmetic, rather than *floating point arithmetic* "
         "rules. As the latter is subject to round-off errors, tests sometimes fail "
         "unexpectedly. Note that for comparing floating point numbers the the standard "
         "library provides a :py:meth:`math.isclose` method."
            , "Another silent assumption by which we can be mislead is in the random numbers. "
              "In fact, :py:meth:`random.random` generates pseudo-random numbers **in the interval "
              "``[0,1[``**, which is quite a bit smaller than ``]-inf,+inf[``. No matter how often "
              "we run the test the special case above that fails will never be encountered, which "
              "may lead to unwarranted confidence in the code."
         ]
    )
    Paragraph(
        "So let us fix the failing test using :py:meth:`math.isclose` to account for round-off "
        "errors by specifying an relative tolerance and negating the condition for the "
        "original test:"
    )
    CodeBlock(
        ['def test_dot_one_2():'
            , '    a1 = 1.0e16'
            , '    a   = [a1 , 1.0, -a1]'
            , '    one = [1.0, 1.0, 1.0]'
            , '    # test:'
            , '    aone = et_dot.dot(a,one)'
            , '    expected = 1.0'
            , '    assert aone != expected'
            , '    assert math.isclose(result, expected, rel_tol=1e-15)'
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    Paragraph(
        "Another aspect that deserves testing the behavior of the code in exceptional "
        "circumstances. Does it indeed raise :py:exc:`ArithmeticError` if the arguments "
        "are not of the same length?"
    )
    CodeBlock(
        ["import pytest"
            , ""
            , "def test_dot_unequal_length():"
            , "    a = [1,2]"
            , "    b = [1,2,3]"
            , "    with pytest.raises(ArithmeticError):"
            , "        et_dot.dot(a,b)"
         ]
        , language='python', copyto=project_path / 'tests/test_et_dot.py', append=True
    )
    Paragraph(
        "Here, :py:meth:`pytest.raises` is a *context manager* that will verify that "
        ":py:exc:`ArithmeticError` is raise when its body is executed. The test will "
        "succeed if indeed the code raises :py:exc:`ArithmeticError` and raise "
        ":py:exc:`AssertionErrorError` if not, causing the test to fail. For an "
        "explanation fo context managers see "
        "`The Curious Case of Python's Context Manager <https://rednafi.github.io/digressions/python/2020/03/26/python-contextmanager.html>`_."
        "Note that you can easily make :meth:`et_dot.dot` raise other exceptions, e.g. "
        ":exc:`TypeError` by passing in arrays of non-numeric types:"
    )
    CodeBlock(
        ["import et_dot"
            , "et_dot.dot([1,2],[1,'two'])"
            , "del et_dot #hide#"
         ]
        , language='pycon', execute=True, cwd=project_path, error_ok=True
    )
    Paragraph(
        "Note that it is not the product ``a[i]*b[i]`` for ``i=1`` that is wreaking havoc, "
        "but the addition of its result to ``d``. Furthermore, Don't bother the link to "
        "where the error occured in the traceback. It is due to the fact that this course "
        "is completely generated with Python rather than written by hand)."
    )
    Paragraph(
        "More tests could be devised, but the current tests give us sufficient confidence. "
        "The point where you stop testing and move on with the next issue, feature, or "
        "project is subject to various considerations, such as confidence, experience, "
        "problem understanding, and time pressure. In any case this is a good point to "
        "commit changes and additions, increase the version number string, and commit the "
        "version bumb as well:"
    )
    CodeBlock(
        ["git commit -a -m 'dot() tests added'"
            , "micc2 version -p"
            , "git commit -a -m 'v0.0.1'"
         ]
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "The the ``micc2 version`` flag ``-p`` is shorthand for ``--patch``, and requests "
        "incrementing the patch (=last) component of the version string, as seen in the "
        "output. The minor component can be incremented with ``-m`` or ``--minor``, the "
        "major component with ``-M`` or ``--major``. "
    )
    Paragraph(
        "At this point you might notice that even for a very simple and well defined "
        "function, as the dot product, the amount of test code easily exceeds the amount "
        "of tested code by a factor of 5 or more. This is not at all uncommon. As the "
        "tested code here is an isolated piece of code, you will probably leave it alone "
        "as soon as it passes the tests and you are confident in the solution. If at some "
        "point, the :py:meth:`dot` would failyou should add a test that reproduces the error "
        "and improve the solution so that it passes the test."
    )
    Paragraph(
        "When constructing software for more complex problems, there will be several "
        "interacting components and running the tests after modifying one of the components "
        "will help you assure that all components still play well together, and spot problems "
        "as soon as possible."
    )

    Heading('Improving efficiency', level=3, crosslink='improving-efficiency')

    Paragraph(
        "There are times when a just a correct solution to the problem at hand is"
        "sufficient. If ``ET-dot`` is meant to compute a few dot products of small "
        "arrays, the naive implementation above will probably be sufficient. "
        "However, if it is to be used many times and for large arrays and the user "
        "is impatiently waiting for the answer, or if your computing resources are "
        "scarse, a more efficient implementation is needed. Especially in scientific "
        "computing and high performance computing, where compute tasks may run for days "
        "using hundreds or even thousands of of compute nodes and resources are to be "
        "shared with many researchers, using the resources efficiently is of utmost "
        "importance and efficient implementations are therefore indispensable."
    )
    Paragraph(
        "However important efficiency may be, it is nevertheless a good strategy for "
        "developing a new piece of code, to start out with a simple, even naive "
        "implementation, neglecting efficiency considerations totally, instead "
        "focussing on correctness. Python has a reputation of being an extremely "
        "productive programming language. Once you have proven the correctness of "
        "this first version it can serve as a reference solution to verify the "
        "correctness of later more efficient implementations. In addition, the "
        "analysis of this version can highlight the sources of inefficiency and "
        "help you focus your attention to the parts that really need it."
    )

    Heading('Timing your code', level=4, crosslink='timing-code')

    Paragraph(
        "The simplest way to probe the efficiency of your code is to time it: write "
        "a simple script and record how long it takes to execute. Here's a script "
        "that computes the dot product of two long arrays of random numbers."
    )
    CodeBlock(
        ['"""File prof/run1.py"""'
            , 'import sys              #hide#'
            , 'sys.path.insert(0,".")  #hide#'
            , 'import random'
            , 'from et_dot import dot # the dot method is all we need from et_dot'
            , ''
            , 'def random_array(n=1000):'
            , '    """Create an array with n random numbers in [0,1[."""'
            , '    # Below we use a list comprehension (a Python idiom for '
            , '    # creating a list from an iterable object).'
            , '    a = [random.random() for i in range(n)]'
            , '    return a'
            , ''
            , 'if __name__==\'__main__\':'
            , '    a = random_array()'
            , '    b = random_array()'
            , '    print(dot(a, b))'
            , '    print("-*# done #*-")'
         ]
        , language='python', copyto=project_path / 'prof/run1.py'
    )
    Paragraph(
        "Executing this script yields:"
    )
    CodeBlock(
        "python ./prof/run1.py"
        , language='bash', execute=True, cwd=project_path
    )
    Note(
        "Every run of this script yields a slightly different outcome because "
        "we did not fix ``random.seed()``. It will, however, typically be around "
        "250. Since the average outcome of ``random.random()`` is 0.5, so every "
        "entry contributes on average ``0.5*0.5 = 0.25`` and as there are 1000 "
        "contributions, that makes on average 250.0."
    )
    Paragraph(
        "We are now ready to time our script. There are many ways to achieve this. "
        "Here is a `particularly good introduction <https://realpython.com/python-timer/>`_. "
        "The `et-stopwatch project <https://et-stopwatch.readthedocs.io/en/latest/readme.html>`_ "
        "takes this a little further. It can be installed in your current Python environment "
        "with ``pip``:"
    )
    CodeBlock(
        'python -m pip install et-stopwatch'
        , language='bash', execute=True
    )
    Paragraph(
        "Although ``pip`` is complaining a bit about not being up to date, the "
        "installation is successful."
    )
    Paragraph(
        "To time the script above, modify it as below, using the :py:class:`Stopwatch` "
        "class as a context manager:"
    )
    CodeBlock(
        ['"""File prof/run1.py"""'
            , 'import sys              #hide#'
            , 'sys.path.insert(0,".")  #hide#'
            , 'import random'
            , 'from et_dot import dot # the dot method is all we need from et_dot'
            , ''
            , 'from et_stopwatch import Stopwatch'
            , ''
            , 'def random_array(n=1000):'
            , '    """Create an array with n random numbers in [0,1[."""'
            , '    # Below we use a list comprehension (a Python idiom for '
            , '    # creating a list from an iterable object).'
            , '    a = [random.random() for i in range(n)]'
            , '    return a'
            , ''
            , 'if __name__==\'__main__\':'
            , '    with Stopwatch(message="init"):'
            , '        a = random_array()'
            , '        b = random_array()'
            , '    with Stopwatch(message="dot "):'
            , '        a_dot_b = dot(a, b)'
            , '    print(a_dot_b)'
            , '    print("-*# done #*-")'
         ]
        , language='python', copyto=project_path / 'prof/run1.py'
    )
    Paragraph(
        "and execute it again:"
    )
    CodeBlock(
        "python ./prof/run1.py"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "When the script is executed each :py:class:`with` block will print "
        "the time it takes to execute its body. The first :py:class:`with` "
        "block times the initialisation of the arrays, and the second times "
        "the computation of the dot product. Note that the initialization of "
        "the arrays takes a bit longer than the dot product computation. "
        "Computing random numbers is expensive."
    )

    Heading("Comparison to Numpy", level=4, crosslink='comparison-numpy')

    Paragraph(
        "As said earlier, our implementation of the dot product is rather "
        "naive. If you want to become a good programmer, you should understand "
        "that you are probably not the first researcher in need of a dot product "
        "implementation. For most linear algebra problems, Numpy_ provides very "
        "efficient implementations.Below the modified :file:`run1.py` script adds "
        "timing results for the Numpy_ equivalent of our code."
    )
    CodeBlock(
        ['"""File prof/run1.py"""'
            , 'import sys                                                           #hide#'
            , 'sys.path.insert(0,".")                                               #hide#'
            , 'import random                                                        #hide#'
            , 'from et_dot import dot # the dot method is all we need from et_dot   #hide#'
            , 'from et_stopwatch import Stopwatch                                   #hide#'
            , 'def random_array(n=1000):                                            #hide#'
            , '    """Create an array with n random numbers in [0,1[."""            #hide#'
            , '    # Below we use a list comprehension (a Python idiom for          #hide#'
            , '    # creating a list from an iterable object).                      #hide#'
            , '    a = [random.random() for i in range(n)]                          #hide#'
            , '    return a                                                         #hide#'
            , '# ...'
            , 'import numpy as np'
            , ''
            , 'if __name__==\'__main__\':'
            , '    with Stopwatch(message="et init"):'
            , '        a = random_array()'
            , '        b = random_array()'
            , '    with Stopwatch(message="et dot "):'
            , '        dot(a,b)'
            , '    with Stopwatch(message="np init"):'
            , '        a = np.random.rand(1000)'
            , '        b = np.random.rand(1000)'
            , '    with Stopwatch(message="np dot "):'
            , '        np.dot(a,b)'
            , '    print("-*# done #*-")'
         ]
        , language='python', copyto=project_path / 'prof/run1.py'
    )
    Paragraph(
        "Its execution yields:"
    )
    CodeBlock(
        "python ./prof/run1.py"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "Obviously, numpy does significantly better than our naive dot product "
        "implementation. It completes the dot product in 7.5% of the time. It is "
        "important to understand the reasons for this improvement:"
    )
    List(
        ["Numpy_ arrays are contiguous data structures of floating point numbers, "
         "unlike Python's :py:class:`list` which we have been using for our arrays, "
         "so far. In a Python :py:class:`list` object is in fact a pointer that can "
         "point to an arbitrary Python object. The items in a Python :py:class:`list` "
         "object may even belong to different types. Contiguous memory access is far "
         "more efficient. In addition, the memory footprint of a numpy array is "
         "significantly lower that that of a plain Python list."
            , "The loop over Numpy_ arrays is implemented in a low-level programming "
              "languange, like C, C++ or Fortran. This allows to make full use of the "
              "processors hardware features, such as *vectorization* and "
              "*fused multiply-add* (FMA)."
         ]
    )
    Note(
        "Note that also the initialisation of the arrays with numpy is almost 6 times "
        "faster, for roughly the same reasons."
    )

    Heading('Conclusion', level=4, crosslink='conclusion')

    Paragraph(
        "There are three important generic lessons to be learned from this tutorial:"
    )
    List(
        ["Always start your projects with a simple and straightforward implementation which "
         "can be easily be proven to be correct, even if you know that it will not satisfy "
         "your efficiency constraints. You should use it as a reference solution to prove the "
         "correctness of later more efficient implementations."
            , "Write test code for proving correctness. Tests must be reproducible, and be run "
              "after every code extension or modification to ensure that the changes did not "
              "break the existing code."
            , "Time your code to understand which parts are time consuming and which not. "
              "Optimize bottlenecks first and do not waste time optimizing code that does "
              "not contribute significantly to the total runtime. Optimized code is typically "
              "harder to read and may become a maintenance issue."
            , 'Before you write any code, in this case our dot product implementation, spend '
              'some time searching the internet to see what is already available. Especially '
              'in the field of scientific and high performance computing there are many excellent '
              'libraries available which are hard to beat. Use your precious time for new stuff. '
              'Consider adding new features to an existing codebase, rather than starting from '
              'scratch. It will improve your programming skills and gain you time, even though '
              'initially your progress may seem slower. It might also give your code more '
              'visibility, and more users, because you provide them with and extra feature on '
              'top of something they are already used to.'
         ]
        , numbered=True
    )

    Heading('Binary extension modules', level=2, crosslink='tutorial-3')

    Heading('Introduction - High Performance Python', level=3, crosslink='intro-HPPython')
    Paragraph(
        "Suppose for a moment that our dot product implementation :py:meth:`et_dot.dot()` "
        "we developed in tutorial-2` is way too slow to be practical for the research "
        "project that needs it, and that we did not have access to fast dot product "
        "implementations, such as :py:meth:`numpy.dot()`. The major advantage we took "
        "from Python is that coding :py:meth:`et_dot.dot()` was extremely easy, and even "
        "coding the tests wasn't too difficult. In this tutorial you are about to discover "
        "that coding a highly efficient replacement for :py:meth:`et_dot.dot()` is not too "
        "difficult either. There are several approaches for this. Here are a number of "
        "highly recommended links covering them:"
    )
    List(
        [
            "`Why you should use Python for scientific research <https://developer.ibm.com/dwblog/2018/use-python-for-scientific-research/>`_"
            ,
            "`Performance Python: Seven Strategies for Optimizing Your Numerical Code <https://www.youtube.com/watch?v=zQeYx87mfyw>`_"
            , "`High performance Python 1 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-1>`_"
            , "`High performance Python 2 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-2>`_"
            , "`High performance Python 3 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-3>`_"
            , "`High performance Python 4 <http://www.admin-magazine.com/HPC/Articles/High-Performance-Python-4>`_"
            ]
    )
    Paragraph(
        "Two of the approaches discussed in the *High Performance Python* series involve "
        "rewriting your code in Modern Fortran or C++ and generate a shared library that "
        "can be imported in Python just as any Python module. This is exactly the approach "
        "taken in important HPC Python modules, such as Numpy_, pyTorch_ and pandas_."
        "Such shared libraries are called *binary extension modules*. Constructing binary "
        "extension modules is by far the most scalable and flexible of all current "
        "acceleration strategies, as these languages are designed to squeeze the maximum of "
        "performance out of a CPU."
    )
    Paragraph(
        "However, figuring out how to build such binary extension modules is a bit of a "
        "challenge, especially in the case of C++. This is in fact one of the main reasons "
        "why Micc2_ was designed: facilitating the construction of binary extension modules "
        "and enabling the developer to create high performance tools with ease. To that end, "
        "Micc2_ can provide boilerplate code for binary extensions as well a practical wrapper "
        "for building the binary extension modules, the ``micc2 build`` command. This command "
        "uses CMake_ to pass the build options to the compiler, while bridging the gap between "
        "C++ and Fortran, on one hand and Python on the other hand using pybind11_ and f2py_. "
        "respectively. This is illustrated in the figure below:"
    )
    Image('../tutorials/im-building.png')
    Paragraph(
        "There is a difference in how f2py_ and pybind11_ operate. F2py_ is an *executable* "
        "that inspects the Fortran source code and creates wrappers for the subprograms it finds. "
        "These wrappers are C code, compiled and linked with the compiled Fortran code to build "
        "the extension module. Thus, f2py_ needs a Fortran compiler, as well as a C compiler. "
        "The Pybind11_ approach is conceptually simpler. Pybind11_is a *C++ template library* "
        "that the programmer uses to express the interface between Python and C++. In fact the "
        "introspection is done by the programmer, and there is only one compiler round, using a "
        "C++ compiler. This gives the programmer more flexibility and control, but also a bit "
        "more work."
    )

    Heading('Choosing between Fortran and C++ for binary extension modules', level=4, crosslink='f90-or-cpp')

    Paragraph(
        "Here are a number of arguments that you may wish to take into account for choosing the "
        "programming language for your binary extension modules:"
    )
    List(
        ["Fortran is a simpler language than C++."
            , "It is easier to write efficient code in Fortran than C++."
            , "C++ is a general purpose language (as is Python), whereas Fortran is meant for "
              "scientific computing. Consequently, C++ is a much more expressive language."
            , "C++ comes with a huge standard library, providing lots of data structures and "
              "algorithms that are hard to match in Fortran. If the standard library is not "
              "enough, there are also the highly recommended `Boost <https://boost.org>`_ "
              "libraries and many other high quality domain specific libraries. There are also "
              "domain specific libraries in Fortran, but their count differs by an order of "
              "magnitude at least."
            , "With Pybind11_ you can almost expose anything from the C++ side to Python, and "
              "vice versa, not just functions."
            , "Modern Fortran is (imho) not as good documented as C++. Useful places to look "
              "for language features and idioms are:"
         ]
    )
    List(
        ['Fortran: https://www.fortran90.org/'
            , 'C++: http://www.cplusplus.com/'
            , 'C++: https://en.cppreference.com/w/'
         ]
        , indent=4
    )
    Paragraph(
        "In short, C++ provides much more possibilities, but it is not for the novice. "
        "As to my own experience, I discovered that working on projects of moderate "
        "complexity I progressed significantly faster using Fortran rather than C++, "
        "despite the fact that my knowledge of Fortran is quite limited compared to C++. "
        "However, your mileage may vary."
    )

    Heading('Adding Binary extensions to a Micc2_ project', level=3, crosslink='add-bin-ext')

    Paragraph(
        "Adding a binary extension to your current project is simple. To add a binary "
        "extension 'foo' written in (Modern) Fortran, run:"
    )
    CodeBlock(
        "micc add foo --f90"
        , language='bash'
    )
    Paragraph(
        "and for a C++ binary extension, run:"
    )
    CodeBlock(
        "micc add bar --cpp"
        , language='bash'
    )
    Paragraph(
        "The ``add`` subcommand adds a component to your project. It specifies a name, "
        "here, ``foo``, and a flag to specify the kind of the component, ``--f90`` for a "
        "Fortran binary extension module, ``--cpp`` for a C++ binary extension module. "
        "Other components are a Python sub-module with module structure (``--module``), "
        "or package structure ``--package``, and a CLI script (`--cli` and `--clisub`). "
    )
    Paragraph(
        "You can add as many components to your code as you want. However, the project "
        "must have a *package* structure (see :ref:`modules-and-packages` for how to "
        "convert a project with a *module* structure)."
    )
    Paragraph(
        "The binary modules are build with the ``micc2 build`` command. :"
    )
    CodeBlock(
        "micc2 build foo"
        , language='bash'
    )
    Paragraph(
        "This builds the Fortran binary extension :file:`foo`. To build all binary "
        "extensions at once, just issue ``micc2 build``."
    )
    Paragraph(
        "As Micc2_ always creates complete working examples you can build the "
        "binary extensions right away and run their tests with pytest_"
    )
    Paragraph(
        "If there are no syntax errors the binary extensions will be built, "
        "and you will be able to import the modules :py:mod:`foo` and "
        ":py:mod:`bar` in your project scripts and use their subroutines "
        "and functions. Because :py:mod:`foo` and :py:mod:`bar` are "
        "submodules of your micc_ project, you must import them as:"
    )
    CodeBlock(
        ["import my_package.foo"
            , "import my_package.bar"
            , ""
            , "# call foofun in my_package.foo" \
            , "my_package.foo.foofun(...)"
            , ""
            , "# call barfun in my_package.bar" \
            , "my_package.bar.barfun(...)"
         ]
    )

    Heading('Build options', level=4, crosslink='micc2-build-options')

    Paragraph(
        "Here is an overview of ``micc2 build`` options:"
    )
    CodeBlock(
        "micc2 build --help"
        , language='bash', execute=True
    )

    Heading('Building binary extension modules from Fortran', level=3, crosslink='building-f90')

    Paragraph(
        'So, in order to implement a more efficient dot product, let us add a Fortran '
        'binary extension module with name ``dotf``:'
    )
    # CodeBlock(
    #     "micc2 add dotf --f90"
    #     , language='bash', execute=True, cwd=project_path, error_ok=True
    # )
    # Paragraph(
    #     "For Micc2 to be able to add components to a project, the project must "
    #     "have package structure. We did not foresee that when we created the "
    #     ":file:`ET-dot` project with a module structure, but, fortunately, Micc2 "
    #     "can convert it:"
    # )
    # CodeBlock(
    #     "micc2 convert-to-package --overwrite"
    #     , language='bash', execute=True, cwd=project_path, error_ok=True
    # )
    # Paragraph(
    #     "(See the :ref:`modules-and-packages` section for the meaning of the "
    #     "``--overwrite`` flag). We can now run the ``micc2 add`` command again:"
    # )
    CodeBlock(
        "micc2 add dotf --f90"
        , language='bash', execute=True, cwd=project_path, error_ok=True
    )
    Paragraph(
        "The command now runs successfully, and the output tells us where to "
        "enter the Fortran source code, the build settings, the test code and "
        "the documentation of the added module. Everything related to the "
        ":file:`dotf` sub-module is in subdirectory :file:`ET-dot/et_dot/f90_dotf`. "
        "That directory has a ``f90_`` prefix indicating that it relates to a "
        "Fortran binary extension module. As useal, these files contain "
        "already working example code that you an inspect to learn how things "
        "work."
    )
    Paragraph(
        "Let's continue our development of a Fortran version of the dot product. "
        "Open file :file:`ET-dot/et_dot/f90_dotf/dotf.f90` in your favorite editor "
        "or IDE and replace the existing example code in the Fortran source file with:"
    )
    CodeBlock(
        language='fortran'
        , copyfrom=snippets / 'dotf.f90'
        , copyto=project_path / 'et_dot/f90_dotf/dotf.f90'
    )
    Paragraph(
        "The binary extension module can now be built:"
    )
    CodeBlock(
        "micc2 build dotf"
        , language='bash', execute=True, cwd=project_path
    )

    Paragraph(
        f"The command produces a lot of output, which comes from CMake, f2py, the"
        f"compilation of the Fortran code, and the compilation of the wrappers of "
        f"the fortran code, which are written in C."
        f"If there are no syntax errors in the Fortran code, the binary extension "
        f"module will build successfully, as above and be installed in a the "
        f"package directory of our project :file:`ET-dot/et_dot`. The full module "
        f"name is :file:`dotf{extension_suffix}`. The extension is composed of: "
        f"the kind of Python distribution (``{pydist[1:]}``), the MAJORminor version "
        f"string of the Python version being used (``{pyver}`` as we are running "
        f"Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}), "
        f"the OS on which we are working (``{os}``), and an extension indicating "
        f"a shared library on this OS (``.{soext}``). This file can be imported "
        f"in a Python script, by using the filename without the extension, i.e. "
        f"``dotf``. As the module was built successfully, we can test it. Here is "
        f"some test code. Enter it in file :file:`ET-dot/tests/test_f90_dotf.py`:"
    )
    CodeBlock(
        ['import numpy as np'
            , 'import et_dot'
            , '# create an alias for the dotf binary extension module'
            , 'f90 = et_dot.dotf'
            , ''
            , 'def test_dot_aa():'
            , '    # create an numpy array of floats:'
            , '    a = np.array([0,1,2,3,4],dtype=float)'
            , '    # use the original dot implementation to compute the expected result:'
            , '    expected = et_dot.dot(a,a)'
            , '    # call the dot function in the binary extension module with the same arguments:'
            , '    a_dot_a = f90.dot(a,a)'
            , '    assert a_dot_a == expected'
         ]
        , language='Python', copyto=project_path / 'tests/test_f90_dotf.py'
    )
    Paragraph(
        "Then run the test (we only run the test for the dotf module, as "
        "we did not touch the :py:meth:`et_dot.dot` implementation):"
    )
    CodeBlock(
        "pytest tests/test_f90_dotf.py"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "The astute reader will notice the magic that is happening here: "
        "``a`` is a numpy array, which is passed as the first and second "
        "parameter to the :py:meth:`et_dot.dotf.dot` function defined in "
        "our binary extension module. Note that the third parameter of "
        "the :py:meth:`et_dot.dotf.dot` function is omitted. How did that "
        "happen? The ``micc2 build`` command uses f2py_ to build the binary "
        "extension module. When calling :py:meth:`et_dot.dotf.dot` you are "
        "in fact calling a wrapper function that f2py created that extracts "
        "the pointer to the memory of array ``a`` and its length. The wrapper "
        "function then calls the Fortran function with the approprioate "
        "parameters as specified in the Fortran function definition. This "
        "invisible wrapper function is in fact rather intelligent, it even "
        "handles type conversions. E.g. we can pass in a Python array, and "
        "the wrapper will convert it into a numpy array, or an array of ints, "
        "and the wrapper will convert it into a float array. In fact the "
        "wrapper considers all implicit type conversions allowed by Python. "
        "However practical this feature may be, type conversion requires "
        "copying the entire array and converting each element. For long "
        "arrays this may be prohibitively expensive. For this reason the "
        ":file:`et_dot/f90_dotf/CMakeLists.txt` file specifies the "
        "``F2PY_REPORT_ON_ARRAY_COPY=1`` flag which makes the wrappers issue a "
        "warning to tell you that you should modify the client program to pass "
        "types to the wrapper which to not require conversion."
    )
    CodeBlock(
        ['import et_dot'
            , 'from importlib import reload                             #hide#'
            , 'et_dot = reload(et_dot)                                  #hide#'
            , 'a = [1,2,3]'
            , 'b = [2,2,2]'
            , 'print(et_dot.dot(a,b))'
            , 'print(et_dot.dotf.dot(a,b))'
            , 'print("created an array from object",file=sys.stderr)    #hide#'
            , 'print("created an array from object",file=sys.stderr)    #hide#'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    # For some reason the error message 'created an array from object' is not
    # captured by python. we faked it with a hidden print stmt.

    Paragraph(
        "Here, ``a`` and ``b`` are plain Python lists, not numpy arrays, and"
        "they contain ``int`` numbers. :py:meth:`et_dot.dot()` therefore also "
        "returns an int (``12``). However, the Fortran implementation "
        ":py:meth:`et_dot.dotf.dot()` expects an array of floats and returns a "
        "float (``12.0``). The wrapper converts the Python lists ``a`` and ``b`` "
        "to numpy ``float`` arrays. If the binary extension module was compiled "
        "with ``F2PY_REPORT_ON_ARRAY_COPY=1`` (the default setting) the wrapper "
        "will warn you with the message``created an array from object``. If we "
        "construct the numpy arrays ourselves, but still of type ``int``, the "
        "wrapper has to convert the ``int`` array into a ``float`` array, because "
        "that is what corresponds the the Fortran ``real*8`` type, and will "
        "warn that it *copied* the array to make the conversion:"
    )
    CodeBlock(
        ['import et_dot'
            , 'import numpy as np'
            , 'from importlib import reload                                 #hide#'
            , 'et_dot = reload(et_dot)                                      #hide#'
            , 'a = np.array([1,2,3])'
            , 'b = np.array([2,2,2])'
            , 'print(et_dot.dot(a,b))'
            , 'print(et_dot.dotf.dot(a,b))'
            , 'print("copied an array: size=3, elsize=8", file=sys.stderr)  #hide#'
            , 'print("copied an array: size=3, elsize=8", file=sys.stderr)  #hide#'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    # For some reason the error message 'copied an array: size=3, elsize=8' is
    # not captured by python. we faked it with a hidden print stmt.
    Paragraph(
        "Here, ``size`` refers to the length of the array, and elsize is the"
        "number of bytes needed for each element of the target array type, c.q. "
        "a ``float``."
    )
    Note(
        "The wrappers themselves are generated in C code, so, you not only need "
        "a Fortran compiler, but also a C compiler."
    )
    Paragraph(
        "Note that the test code did not explicitly import :py:mod:`et_dot.dotf`, "
        "just :py:mod:`et_dot`. This is only possible because Micc2 has modified "
        ":file:`et_dot/__init__.py` to import every submodule that has been added "
        "to the project:"
    )
    CodeBlock(
        ['# in file et_dot/__init__.py'
            , 'import et_dot.dotf'
         ]
        , language='python'
    )
    Paragraph(
        "If the submodule :py:mod:`et_dot.dotf` was not built or failed to build, "
        "that import statement will fail and raise a :py:exc:`ModuleNotFoundError` "
        "exception. Micc2 has added a little extra magic to attempt to build the "
        "module automatically in that case:"
    )
    CodeBlock(
        ['# in file et_dot/__init__.py'
            , 'try:'
            , '    import et_dot.dotf'
            , 'except ModuleNotFoundError as e:'
            , '    # Try to build this binary extension:'
            , '    from pathlib import Path'
            , '    import click'
            , '    from et_micc2.project import auto_build_binary_extension'
            , '    msg = auto_build_binary_extension(Path(__file__).parent, "dotf")'
            , '    if not msg:'
            , '        import et_dot.dotf'
            , '    else:'
            , '        click.secho(msg, fg="bright_red")'
         ]
        , language='python'
    )
    Paragraph(
        "Obviously, you should also add the other "
        "tests we created for the Python implementation. "
    )
    process(doc)


class FilterCMakeLists:
    def __init__(self, startline, stopline):
        self.startline = listify(startline)
        self.stopline = listify(stopline)

    def __call__(self, lines):
        nsections = len(self.stopline)
        omitted = '...                                                         # (boilerplate code omitted for clarity)'
        lines_kept = [omitted]
        start = False
        section = 0
        for line in lines:
            stop = start and line.startswith(self.stopline[section])
            if stop:
                lines_kept.append(omitted)
                start = False
                section += 1
                if section == nsections:
                    break
            if not start:
                start = line.startswith(self.startline[section])
            if start:
                if line.strip():
                    lines_kept.append(line)
        return lines_kept


def TutorialProject_et_dot_2():
    doc = RstDocument('TutorialProject_et_dot_2', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading("Dealing with Fortran modules", level=4, crosslink='f90-modules')

    Paragraph(
        "Modern Fortran has a *module* concept of its own. This may be a bit confusing, "
        "as we have been talking about modules in a Python context, so far. The Fortran "
        "module is meant to group variable and procedure definitions that conceptually "
        "belong together. Inside fortran they are comparable to C/C++ header files. Here "
        "is an example:"
    )
    CodeBlock(
        ['MODULE my_f90_module'
            , 'implicit none'
            , 'contains'
            , '  function dot(a,b,n)'
            , '  ! Compute the dot product of a and b'
            , '    implicit none'
            , '  !'
            , '  !-----------------------------------------------'
            , '    integer*4              , intent(in)    :: n'
            , '    real*8   , dimension(n), intent(in)    :: a,b'
            , '    real*8                                 :: dot'
            , '  ! declare local variables'
            , '    integer*4 :: i'
            , '  !-----------------------------------------------'
            , '    dot = 0.'
            , '    do i=1,n'
            , '        dot = dot + a(i) * b(i)'
            , '    end do'
            , '  end function dot'
            , 'END MODULE my_f90_module'
         ]
        , language='fortran', copyto=project_path / 'et_dot/f90_dotf/dotf.f90'
    )
    CodeBlock(
        "micc2 build --clean"
        , language='bash', execute=True, cwd=project_path, hide=True
    )
    Paragraph(
        "F2py translates the module containing the Fortran ``dot`` definition into "
        "an extra *namespace* appearing in between the :py:mod:`dotf` Python submodule "
        "and the :py:meth:`dot` function, which is found in ``et_dot.dotf.my_f90_module`` "
        "instead of in ``et_dot.dotf``."
    )
    CodeBlock(
        ['import numpy as np'
            , 'import et_dot'
            , 'from importlib import reload                                 #hide#'
            , 'et_dot.dotf = reload(et_dot.dotf)                            #hide#'
            , 'a = np.array([1.,2.,3.])'
            , 'b = np.array([2.,2.,2.])'
            , 'print(et_dot.dotf.my_f90_module.dot(a,b))'
            , '# If typing this much annoys you, you can create an alias to the `Fortran module`:'
            , 'f90 = et_dot.dotf.my_f90_module'
            , 'print(f90.dot(a,b))'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    Paragraph(
        "This time there is no warning from the wrapper as ``a`` and ``b`` are "
        "numpy arrays of type ``float``, which correspond to Fortran's ``real*8``, "
        "so no conversion is needed."
    )

    Heading('Controlling the build', level=4, crosslink='control-build-f90')

    Paragraph(
        "The build parameters for our Fortran binary extension module are "
        "detailed in the file :file:`et_dot/f90_dotf/CMakeLists.txt`. This "
        "is a rather lengthy file, but most of it is boilerplate code which "
        "you should not need to touch. The boilerplate sections are clearly "
        "marked. By default this file specifies that a release version is to "
        "be built. The file documents a set of CMake variables that can be "
        "used to control the build type:"
    )
    List(
        ["CMAKE_BUILD_TYPE : DEBUG | MINSIZEREL | RELEASE* | RELWITHDEBINFO"
            , "F2PY_noopt : turn off optimization options"
            , "F2PY_noarch : turn off architecture specific optimization options"
            , "F2PY_f90flags : additional compiler options"
            , "F2PY_arch : architecture specific optimization options"
            , "F2PY_opt : optimization options"
         ]
    )
    Paragraph(
        "In addition you can specify:"
    )
    List(
        ['preprocessor macro definitions'
            , 'include directories'
            , 'link directories'
            , 'link libraries'
         ]
    )
    Paragraph(
        "Here are the sections of :file:`CMakeLists.txt` to control the build. "
        "Uncomment the relevant lines and modify them to your needs."
    )
    CodeBlock(
        []
        ,
        copyfrom=workspace / '../et-micc2/' / 'et_micc2/templates/module-f90/{{cookiecutter.project_name}}/{{cookiecutter.package_name}}/f90_{{cookiecutter.module_name}}/CMakeLists.txt'
        , filter=FilterCMakeLists
        (startline=['# Set the build type:', '##########']
         , stopline=['#<< begin boilerplate code', '# only boilerplate code below']
         )
    )

    Heading('Building binary extensions from C++', level=3, crosslink='building-cpp')

    Paragraph(
        "To illustrate building binary extension modules from C++ code, let us also "
        "create a C++ implementation for the dot product. Analogously to our "
        ":py:mod:`dotf` module we will call the C++  module :py:mod:`dotc`, where the "
        "``c`` refers to C++, naturally."
    )
    Paragraph(
        "Use the ``micc2 add`` command to add a cpp module:"
    )
    CodeBlock(
        "micc2 add dotc --cpp"
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "As before, the output tells us where we need to add the details of the "
        "component we added to our project. "
    )
    Paragraph(
        "Numpy does not have an equivalent of F2py_ to create wrappers for C++ "
        "code. Instead, Micc2_ uses Pybind11_ to generate the wrappers. For an "
        "excellent overview of this topic, check out "
        "`Python & C++, the beauty and the beast, dancing together <https://channel9.msdn.com/Events/CPP/CppCon-2016/CppCon-2016-Introduction-to-C-python-extensions-and-embedding-Python-in-C-Apps>`_. "
        "Pybind11_ has a lot of 'automagical' features, and the fact that it is a "
        "header-only C++ library makes its use much simpler than, e.g., "
        "`Boost.Python <https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/index.html>`_, "
        "which offers very similar features, but is not header-only and additionally "
        "depends on the python version you want to use. Consequently, you need a "
        "build a :file:`Boost.Python` library for every Python version you want "
        "to use."
    )
    Paragraph(
        "Enter this code in the C++ source file :file:`ET-dot/et_dot/cpp_dotc/dotc.cpp`. "
        "(you may also remove the example code in that file.)"
    )
    CodeBlock(
        []
        , copyfrom=snippets / 'dotc.cpp'
        , language='c++', copyto=project_path / 'et_dot/cpp_dotc/dotc.cpp'
    )
    Paragraph(
        "Obviously the C++ source code is more involved than its Fortran equivalent "
        "in the previous section. This is because f2py_ is a program performing clever "
        "introspection into the Fortran source code, whereas pybind11_ is just "
        "a C++ template library and as such it needs a little help from the user. "
        "This is, however, compensated by the flexibility of Pybind11_."
    )
    Paragraph(
        "We can now build the module:"
    )
    CodeBlock(
        "micc2 build dotc"
        , execute=True, cwd=project_path
    )
    Paragraph(
        f"The ``build`` command produces quit a bit of output, though typically "
        f"less that for a Fortran binary extension module. If the source file does "
        f"not have any syntax errors, and the build did not experience any problems, "
        f"the package directory :file:`et_dot` will contain a binary extension "
        f"module :file:`dotc{extension_suffix}`, along with the previously built "
        f":file:`dotf{extension_suffix}`."
    )
    Paragraph(
        "Here is some test code. It is almost exactly the same as that for the f90 "
        "module :py:mod:`dotf`, except for the module name. Enter the test code in "
        ":file:`ET-dot/tests/test_cpp_dotc.py`:"
    )
    CodeBlock(
        []
        , language='python'
        , copyfrom=snippets / 'test_cpp_dotc.py'
        , copyto=project_path / 'tests/test_cpp_dotc.py'
    )
    Paragraph(
        "The test passes successfully. Obviously, you should also add the other "
        "tests we created for the Python implementation. "
    )
    CodeBlock(
        "pytest tests/test_cpp_dotc.py"
        , execute=True, cwd=project_path
    )
    process(doc)


def TutorialProject_et_dot_3():
    doc = RstDocument('TutorialProject_et_dot_3', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Note(
        "The Pybind11 wrappers automatically apply the same conversions as the "
        "F2py wrappers. Here is an example where the input arrays are a plain "
        "Python ``list`` containing ``int`` values. The wrapper converts them "
        "on the fly into a contiguous array of ``float``valuwa (which correspond "
        "to C++'s ``double``) and returns a ``float``:"
    )
    CodeBlock(
        ['import et_dot'
            , 'print(et_dot.dotc.dot([1,2],[3,4]))'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    Paragraph(
        "This time, however, there is no warning that the wrapper converted or "
        "copied. As converting and copying of large is time consuming, this may "
        "incur a non-negligable cost on your application, Moreover, if the arrays "
        "are overwritten in the C++ code and serve for output, the result will not "
        "be copied back, and will be lost. This will result in a bug in the client "
        "code, as it will continue its execution with the original values. "
    )

    Heading('Controlling the build', level=4, crosslink='control-build-cpp')

    Paragraph(
        "The build parameters for our C++ binary extension module are "
        "detailed in the file :file:`et_dot/cpp_dotc/CMakeLists.txt`, "
        "just as in the f90 case. It contains significantly less boilerplate "
        "code (which you should not need to touch) and provides the same "
        "functionality. Here is the section of "
        ":file:`et_dot/cpp_dotc/CMakeLists.txt` that you might want to adjust "
        "to your needs:"
    )
    CodeBlock(
        []
        ,
        copyfrom=workspace / '../et-micc2/' / 'et_micc2/templates/module-cpp/{{cookiecutter.project_name}}/{{cookiecutter.package_name}}/cpp_{{cookiecutter.module_name}}/CMakeLists.txt'
        , filter=FilterCMakeLists
        (startline=('##########')
         , stopline=('#<< begin boilerplate code')
         )
    )
    Paragraph(
        "Because we need only interface with the C++ compiler, the :file:`CMakeLists.txt` file "
        "is simpler that for the Fortran case."
    )


def TutorialProject_et_dot_4():
    doc = RstDocument('TutorialProject_et_dot_4', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading('Data type issues', level=3, crosslink='data-types')

    Paragraph(
        "When interfacing several programming languages data types require special care. "
        "We already noted that although conversions are automatic if possible, they may "
        "be costly. It is always more computationally efficient that the data types on "
        "both sides (Python and respectively Fortran or C++) correspond. Here is a table "
        "with the most relevant numeric data types in Python, Fortran and C++."
    )
    Table(
        [['data type', 'Numpy(np)/Python', 'Fortran', 'C++']
            , ['unsigned integer', 'np.uint32', 'N/A', 'signed long int']
            , ['unsigned integer', 'np.uint64', 'N/A', 'signed long long int']
            , ['signed integer', 'np.int32, int', 'integer*4', 'signed long int']
            , ['signed integer', 'np.int64', 'integer*8', 'signed long long int']
            , ['floating point', 'np.float32, np,single', 'real*4', 'float']
            , ['floating point', 'np.float64, np.double, float', 'real*8', 'double']
            , ['complex', 'np.complex64', 'complex*4', 'std::complex<float>']
            , ['complex', 'np.complex128', 'complex*8', 'std::complex<double>']
         ]
    )
    Paragraph(
        "If there is automatic conversion between two data types in Python, e.g. "
        "from ``float32`` to ``float64`` the wrappers around our function will "
        "perform the conversion automatically if needed. This happens both for "
        "Fortran and C++. However, this comes with the cost of copying and "
        "converting, which is sometimes not acceptable."
    )
    Paragraph(
        "The result of a Fortran function and a C++ function in a binary "
        "extension module is **always copied** back to the Python variable "
        "that will hold it. As copying large data structures is detrimental "
        "to performance this shoud be avoided. The solution to this problem "
        "is to write Fortran functions or subroutines and C++ functions that "
        "accept the result variable as an argument and modify it in place, "
        "so that the copy operaton is avoided. Consider this example of a "
        "Fortran subroutine that computes the sum of two arrays."
    )
    CodeBlock(
        []
        , language='fortran'
        , copyfrom=snippets / 'dotf-add.f90'
        , copyto=project_path / 'et_dot/f90_dotf/dotf.f90'
    )
    CodeBlock(
        "micc2 build dotf --clean"
        , hide=True
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "The crucial issue here is that the result array ``sumab`` is "
        "qualified as ``intent(inout)``, meaning that the ``add`` "
        "function has both read and write access to it. This function "
        "would be called in Python like this:"
    )
    Paragraph(
        "Let us add this method to our :file:`dotf` binary extension module, "
        "just to demonstrate its use."
    )

    CodeBlock(
        ['import numpy as np'
            , 'import et_dot'
            , 'a = np.array([1.,2.])'
            , 'b = np.array([3.,4.])'
            , 'sum = np.empty(len(a),dtype=float)'
            , 'et_dot.dotf.add(a,b, sum)'
            , 'print(sum)'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    Paragraph(
        "If ``add`` would have been qualified as as ``intent(in)``, as the "
        "input parameters ``a`` and ``b``, ``add`` would not be able to "
        "modify the ``sum`` array. On the other hand, and rather surprisingly, "
        "qualifying it with ``intent(out)`` forces f2py_ to consider the "
        "variable as a left hand side variable and define a wrapper that "
        "in Python would be called like this:"
    )
    CodeBlock(
        'sum = et_dot.dotf.add(a,b)'
        , language='python'
    )
    Paragraph(
        "This obviously implies copying the contents of the result array to "
        "the Python variable :file:`sum`, which, as said, may be prohibitively "
        "expensive."
    )

    process(doc)


def TutorialProject_et_dot_5():
    doc = RstDocument('TutorialProject_et_dot_5', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Paragraph(
        "So, the general advice is: use functions to return only variables of "
        "small size, like a single number, or a tuple, maybe even a small fixed "
        "size array, but certainly not a large array. If you have result variables "
        "of large size, compute them in place in parameters with ``intent(inout)``. "
        "If there is no useful small variable to return, use a subroutine instead "
        "of a function. Sometimes it is useful to have functions return an error "
        "code, or the CPU time the computation used, while the result of the computation "
        "is computed in a parameter with ``intent(inout)``, as below:"
    )
    CodeBlock(copyfrom=snippets / 'dotf-add2.f90'
              , copyto=project_path / 'et_dot/f90_dotf/dotf.f90'
              , language='fortran'
              )
    CodeBlock(
        "micc2 build dotf --clean"
        , hide=True
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "Note that Python does not require you to store the return value of a function. "
        "The above ``add`` function might be called as:"
    )
    CodeBlock(
        ['import numpy as np'
            , 'import et_dot'
            , 'a = np.array([1.,2.])'
            , 'b = np.array([3.,4.])'
            , 'sum = np.empty(len(a),dtype=float)'
            , 'cputime = et_dot.dotf.add(a,b, sum)'
            , 'print(cputime)'
            , 'print(sum)'
         ]
        , language='pycon', execute=True, cwd=project_path
    )

    """

    """
    process(doc)


def TutorialProject_et_dot_6():
    doc = RstDocument('TutorialProject_et_dot_6', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Paragraph(
        "Computing large arrays in place can be accomplished in C++ quite "
        "similarly. As Python does not have a concept of ``const`` parameters, "
        "all parameters are writable by default. However, when casting the "
        "memory of the arrays to pointers, we take care to cast to "
        "``double *`` or ``double const *`` depending on the intended use of"
        "the arrays, in order to prevent errors."
    )
    CodeBlock(copyfrom=snippets / 'dotc-add.cpp'
              , copyto=project_path / 'et_dot/cpp_dotc/dotc.cpp'
              , language='c++'
              )
    CodeBlock(
        "micc2 build dotc --clean"
        , hide=True
        , language='bash', execute=True, cwd=project_path
    )

    process(doc)


def TutorialProject_et_dot_7():
    doc = RstDocument('TutorialProject_et_dot_7', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading('Documenting binary extension modules', level=3, crosslink='document-binary-extensions')

    Paragraph(
        "For Python modules the documentation is automatically extracted from "
        "the doc-strings in the module. However, when it comes to documenting "
        "binary extension modules, this does not seem a good option. Ideally, "
        "the source files :file:`ET-dot/et_dot/f90_dotf/dotf.f90` and "
        ":file:`ET-dot/et_dot/cpp_dotc/dotc.cpp` should document the Fortran "
        "functions and subroutines, and C++ functions, respectively, rather "
        "than the Python interface. Yet, from the perspective of ET-dot being a "
        "Python project, the user is only interested in the documentation of the "
        "Python interface to those functions and subroutines. Therefore, Micc2_ "
        "requires you to document the Python interface in separate :file:`.rst` "
        "files:"
    )
    List(
        [':file:`ET-dot/et_dot/f90_dotf/dotf.rst`'
            , ':file:`ET-dot/et_dot/cpp_dotc/dotc.rst`'
         ]
    )
    Paragraph(
        "their contents could look like this: for :file:`ET-dot/et_dot/f90_dotf/dotf.rst`:"
    )
    CodeBlock(
        ['Module et_dot.dotf'
            , '******************'
            , ''
            , 'Module (binary extension) :py:mod:`dotf`, built from fortran source.'
            , ''
            , '.. function:: dot(a,b)'
            , '   :module: et_dot.dotf'
            , ''
            , '   Compute the dot product of ``a`` and ``b``.'
            , ''
            , '   :param a: 1D Numpy array with ``dtype=float``'
            , '   :param b: 1D Numpy array with ``dtype=float``'
            , '   :returns: the dot product of ``a`` and ``b``'
            , '   :rtype: ``float``'
         ]
        , language='rst'
    )
    Paragraph(
        "and for :file:`ET-dot/et_dot/cpp_dotc/dotc.rst`:"
    )
    CodeBlock(
        ['Module et_dot.dotc'
            , '******************'
            , ''
            , 'Module (binary extension) :py:mod:`dotc`, built from C++ source.'
            , ''
            , '.. function:: dot(a,b)'
            , '   :module: et_dot.dotc'
            , ''
            , '   Compute the dot product of ``a`` and ``b``.'
            , ''
            , '   :param a: 1D Numpy array with ``dtype=float``'
            , '   :param b: 1D Numpy array with ``dtype=float``'
            , '   :returns: the dot product of ``a`` and ``b``'
            , '   :rtype: ``float``'
         ]
        , language='rst'
    )
    Paragraph(
        "The (html) documentation is build as always:"
    )
    CodeBlock(
        "micc2 doc"
        , execute=True, cwd=project_path
    )
    Paragraph(
        "As the output shows, the documentation is found in "
        "your project directory in :file:`docs/_build/html/index.html`. "
        "It can be opened in your favorite browser."
    )
    # we have overwritten dotf and dotc. now we put them back
    CodeBlock(
        hide=True
        , copyfrom=snippets / 'dotf.f90'
        , copyto=project_path / 'et_dot/f90_dotf/dotf.f90'
    )
    CodeBlock(
        hide=True
        , copyfrom=snippets / 'dotc.cpp'
        , copyto=project_path / 'et_dot/cpp_dotc/dotc.cpp'
    )
    CodeBlock(
        'micc2 build --clean'
        , execute=True, cwd=project_path, hide=True
    )

    process(doc)


def TutorialProject_et_dot_8():
    doc = RstDocument('TutorialProject_et_dot_8', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading('Adding Python submodules', level=2, crosslink='python-submodules')

    Paragraph(
        "Adding binary extension (sub)module is important for adding "
        "implementations in Fortran or C++ for performance reasons. "
        "For larger projects it is sometimes practical to be able to "
        "organize your Python code in different files, e.g. one file "
        "for each Python class. Micc2_ allows your to add Python "
        "submodules to your project. These can have a module or a "
        "package stucture. This command adds a module :file:`foo.py` "
        "to your project:"
    )
    CodeBlock(
        "micc2 add foo --py"
        , execute=True, cwd=project_path
    )
    Paragraph(
        "As the output shows, it creates a file :file:`foo.py` in the package "
        "directory :file:`et_dot` of our :file:`ET-dot` project. In this file "
        "you can add all your `foo` related code. Micc2_ ensures that this "
        "submodule is automatically imported in :file:`et_dot`. As usual, Micc2_ "
        "adds working example code, in this case a *hello world* method, named "
        ":py:meth:`greet`:"
    )
    CodeBlock(
        ['import et_dot'
            , 'print(et_dot.foo.greet("from foo"))'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    CodeBlock(
        "micc2 mv foo"
        , execute=True, cwd=project_path
        , hide=True
    )
    Paragraph(
        "Alternatively, we can add a Python submodule with a package structure:"
    )
    CodeBlock(
        "micc2 add foo --package"
        , execute=True, cwd=project_path
    )
    Paragraph(
        "As the output shows, this creates a directory :file:`foo` containing "
        "the file :file:`__init__.py` in the package directory :file:`et_dot` "
        "of our :file:`ET-dot` project, for all your `foo` related code. Again, "
        "Micc2_ ensures that this submodule is automatically imported in "
        ":file:`et_dot` and added working example code, with the same "
        ":py:meth:`greet` meethod as above, which works in exactly the same way:"
    )
    CodeBlock(
        ['import et_dot'
            , 'from importlib import reload     #hide#'
            , 'et_dot = reload(et_dot)          #hide#'
            , 'print(et_dot.foo.greet("from foo"))'
         ]
        , language='pycon', execute=True, cwd=project_path
    )
    Paragraph(
        "Micc2_ also added test code for this submodule in file "
        ":file:`tests/test_foo.py` (irrespective of whether :file:`foo` has a module "
        "or package structure. The test passes, of course:"
    )
    CodeBlock(
        "pytest tests/test_foo.py -s -v"
        , execute=True, cwd=project_path
    )
    CodeBlock(
        "micc2 mv foo"
        , execute=True, cwd=project_path
        , hide=True
    )
    Paragraph(
        "Furthermore. Micc2_ automatically adds documentation entries for submodule "
        ":file:`foo` in :file:`API.rst`. Calling ``micc2 doc`` will automatically "
        "extract documentation from the doc-strings in :file:`foo`. So, writing "
        "doc-strings in :file:`foo.py` or :file:`foo/__init__.py` is all you need "
        "to do."
    )

    Heading('Adding a Python Command Line Interface', level=3, crosslink='clis')

    Paragraph(
        "*Command Line Interfaces* are Python scripts in a Python package that are "
        "installed as executable programs when the package is installed.  E.g. Micc2_ "
        "is a CLI. Installing package :file:`et-micc2` installs the ``micc2`` as an "
        "executable program. CLIs come in two flavors, single command CLIs and CLIs "
        "with subcommands. Single command CLIs perform a single task, which can be "
        "modified by optional parameters and flags. CLIs with subcommands can performs "
        "different, usually related, tasks by selecting an appropriate subcommand. "
        "Git_ and Micc2_ are CLIs with subcommands. You can add a single command CLI "
        "named ``myapp`` to your project with the command:"
    )
    CodeBlock(
        "micc2 add myapp --cli"
        , language='bash'
    )
    Paragraph(
        "and"
    )
    CodeBlock(
        "micc2 add myapp --clisub"
        , language='bash'
    )
    Paragraph(
        "for a CLI with subcommands. Micc2 adds the necessary files, containing "
        "working example code and tests, as well as a documentation entry in "
        ":file:`APPS.rst`. The documentation will be extracted automatically "
        "from doc-strings and help-strings (these are explained below). "
    )

    Heading('CLI example', level=4, crosslink='cli-example')

    Paragraph(
        "Assume that we need quite often to read two arrays from file and "
        "compute their dot product, and that we want to execute this operation as:"
    )
    CodeBlock(
        ["> dotfiles file1 file2"
            , "dot(file1,file2) = 123.456"
         ]
        , language='bash', prompt=''
    )
    Paragraph(
        "The second line is the output that we expect."
    )
    Paragraph(
        ":file:`dotfiles` is, obviously a single command CLI, so we add a CLI "
        "component with the ``--cli`` flag:"
    )
    CodeBlock(
        "micc2 add dotfiles --cli"
        , execute=True, cwd=project_path
    )
    Paragraph(
        "As usual Micc2 tells us where to add the source code for the CLI, and "
        "where to add the test code for it. Furthermore, Micc2_ expects us to use "
        "the Click_ package for implementing the CLI, a very practical and flexible "
        "package which is well documented. The example code in "
        ":file:`et_dot/cli_dotfiles.py` is already based on Click_, and contains an "
        "example of a single command CLI or a Cli with subcommands,m depending on "
        "the flag you used. Here is the proposed implementation of our :file:`dotfiles` "
        "CLI:"
    )
    CodeBlock(lines=[]
              , language='python'
              , copyfrom=snippets / 'cli_dotfiles.py'
              , copyto=project_path / 'et_dot/cli_dotfiles.py'
              )
    Paragraph(
        "Click_ uses decorators to add arguments and options to turn a method, here "
        ":file:`main()` in to the command. Understanding decorators is not really "
        "necessary, but if you are intrigued, check out "
        "`Primer on Python decorators <https://realpython.com/primer-on-python-decorators/>`_. "
        "Otherwise, just follow the Click_ documentation for how to use the Click_ "
        "decorators to create nice CLIs. "
    )
    for i in (1, 2):
        CodeBlock(lines=[]
                  , copyfrom=snippets / f'array{i}.txt'
                  , copyto=project_path / f'tests/array{i}.txt'
                  , hide=True
                  )
    Paragraph(
        "Click_ provides a lot of practical features, such as an automatic help "
        "function which is built from the doc-string of the command method, and "
        "the ``help`` parameters of the options. Sphinx_click_ does the same to "
        "extract documentation for your CLI."
    )
    CodeBlock(
        ["python et_dot/cli_dotfiles.py --help"
            , "python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt"
            , "python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt -v"
            , "python et_dot/cli_dotfiles.py tests/array1.txt tests/array2.txt -vv"
         ]
        , language='bash', execute=True, cwd=project_path
    )
    Paragraph(
        "Here, we did not exactly call the CLI as ``dotfiles``, but that is "
        "because the package is not yet installed. The installed executable "
        "``dotfiles`` would just wrap the command as ``python path/to/et_dot/cli_dotfiles.py``. "
        "Note, that the verbosity parameter is using a nice Click_ feature: by "
        "adding more ``v`` s the verbosity increases."
    )
    # CodeBlock(
    #     "micc2 mv dot-files"
    #     , execute=True, cwd=project_path
    #     , hide=True
    # )
    process(doc)


if __name__=='__main__':
    i = sys.argv[1]
    tut = f'TutorialProject_et_dot_{i}'
    tut = eval(tut)
    tut()
    print('-*# finished #*-')
