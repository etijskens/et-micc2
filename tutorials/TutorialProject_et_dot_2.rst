.. include:: ../HYPERLINKS.rst

.. _f90-modules:

3.3.1. Dealing with Fortran modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modern Fortran has a *module* concept of its own. This may be a bit confusing, as we have
been talking about modules in a Python context, so far. The Fortran module is meant to
group variable and procedure definitions that conceptually belong together.
Inside fortran they are comparable to C/C++ header files. Here is an example:

.. code-block:: fortran

    MODULE my_f90_module
    implicit none
    contains
      function dot(a,b,n)
      ! Compute the dot product of a and b
        implicit none
      !
      !-----------------------------------------------
        integer*4              , intent(in)    :: n
        real*8   , dimension(n), intent(in)    :: a,b
        real*8                                 :: dot
      ! declare local variables
        integer*4 :: i
      !-----------------------------------------------
        dot = 0.
        do i=1,n
            dot = dot + a(i) * b(i)
        end do
      end function dot
    END MODULE my_f90_module


F2py translates the module containing the Fortran ``dot`` definition into an extra
*namespace* appearing in between the :py:mod:`dotf` Python submodule and the
:py:meth:`dot` function, which is found in ``et_dot.dotf.my_f90_module``
instead of in ``et_dot.dotf``.

.. code-block:: pycon

    >>> import numpy as np
    >>> import et_dot
    >>> a = np.array([1.,2.,3.])
    >>> b = np.array([2.,2.,2.])
    >>> print(et_dot.dotf.my_f90_module.dot(a,b))
    12.0
    >>> # If typing this much annoys you, you can create an alias to the `Fortran module`:
    >>> f90 = et_dot.dotf.my_f90_module
    >>> print(f90.dot(a,b))
    12.0
    
This time there is no warning from the wrapper as ``a`` and ``b`` are numpy arrays of
type ``float``, which correspond to Fortran's ``real*8``, so no conversion is
needed.

.. _control-build-f90:

3.3.2. Controlling the build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The build parameters for our Fortran binary extension module are detailed in the file
:file:`et_dot/dotf/CMakeLists.txt`. This is a rather lengthy file, but most of it
is boilerplate code which you should not need to touch. The boilerplate sections are
clearly marked. By default this file specifies that a release version is to be built.
The file documents a set of CMake variables that can be used to control the build type:

* CMAKE_BUILD_TYPE : DEBUG | MINSIZEREL | RELEASE* | RELWITHDEBINFO

* F2PY_noopt : turn off optimization options

* F2PY_noarch : turn off architecture specific optimization options

* F2PY_f90flags : additional compiler options

* F2PY_arch : architecture specific optimization options

* F2PY_opt : optimization options

In addition you can specify:

* preprocessor macro definitions

* include directories

* link directories

* link libraries

Here are the sections of :file:`CMakeLists.txt` to control the build. Uncomment the
relevant lines and modify them to your needs.

.. code-block:: 

    ...                                                         # (boilerplate code omitted for clarity)
    # Set the build type:
    #  - If you do not specify a build type, it is Release by default.
    #  - Note that the DEBUG build type will trigger f2py's '--noopt --noarch --debug' options.
    # set(CMAKE_BUILD_TYPE Debug | MinSizeRel | Release | RelWithHDebInfo)
    ...                                                         # (boilerplate code omitted for clarity)
    ####################################################################################################
    ######################################################################### Customization section ####
    # Specify compiler options #########################################################################
    # Uncomment to turn off optimization:
    # set(F2PY_noopt 1)
    # Uncomment to turn off architecture specific optimization:
    # set(F2PY_noarch 1)
    # Set additional f90 compiler flags:
    # set(F2PY_f90flags your_flags_here)
    # set(F2PY_f90flags -cpp)   # enable the C preprocessor (preprocessor directives must appear on the
                                # on the first column of the line).
    # Set architecture specific optimization compiler flags:
    # set(F2PY_arch your_flags_here)
    # Overwrite optimization flags
    # set(F2PY_opt your_flags_here)
    # Add preprocessor macro definitions ###############################################################
    # add_compile_definitions(
    #     OPENFOAM=1912                     # set value
    #     WM_LABEL_SIZE=$ENV{WM_LABEL_SIZE} # set value from environment variable
    #     WM_DP                             # just define the macro
    # )
    # Add include directories ##########################################################################
    # include_directories(
    #     path/to/dir1
    #     path/to/dir2
    # )
    # Add link directories #############################################################################
    # link_directories(
    #     path/to/dir1
    # )
    # Add link libraries (lib1 -> liblib1.so) ##########################################################
    # link_libraries(
    #     lib1
    #     lib2
    # )
    ####################################################################################################
    ...                                                         # (boilerplate code omitted for clarity)

.. _building-cpp:

3.4. Building binary extensions from C++
----------------------------------------

To illustrate building binary extension modules from C++ code, let us also create a
C++ implementation for the dot product. Analogously to our :py:mod:`dotf` module we
will call the C++  module :py:mod:`dotc`, where the ``c`` refers to C++, naturally.

Use the ``micc2 add`` command to add a cpp module:

.. code-block:: bash

    > micc2 add dotc --cpp
    [INFO]           [ Adding cpp submodule dotc to package et_dot.
    [INFO]               - C++ source in           /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/dotc.cpp.
    [INFO]               - build settings in       /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/CMakeLists.txt.
    [INFO]               - module documentation in /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/dotc.rst (restructuredText format).
    [INFO]               - Python test code in     /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/tests/et_dot/dotc/test_dotc.py.
    [INFO]           ] done.
    

As before, the output tells us where we need to add the details of the component we added
to our project. 

Numpy does not have an equivalent of F2py_ to create wrappers for C++ code. Instead,
Micc2_ uses Pybind11_ to generate the wrappers. For an excellent overview of this
topic, check out
`Python & C++, the beauty and the beast, dancing together <https://channel9.msdn.com/Events/CPP/CppCon-2016/CppCon-2016-Introduction-to-C-python-extensions-and-embedding-Python-in-C-Apps>`_.
Pybind11_ has a lot of 'automagical' features, and the fact that it is a header-only
C++ library makes its use much simpler than, e.g.,
`Boost.Python <https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/index.html>`_,
which offers very similar features, but is not header-only and additionally depends
on the python version you want to use. Consequently, you need a build a
:file:`Boost.Python` library for every Python version you want to use.

Enter this code in the C++ source file :file:`ET-dot/et_dot/dotc/dotc.cpp`. (you
may also remove the example code in that file.)

.. code-block:: c++

    #include <pybind11/pybind11.h>
    #include <pybind11/numpy.h>
    
    double
    dot ( pybind11::array_t<double> a
        , pybind11::array_t<double> b
        )
    {
     // requeest acces to the memory of the Numpy array objects a and b
       auto bufa = a.request()
          , bufb = b.request()
          ;
     // verify dimensions and shape:
        if( bufa.ndim != 1 || bufb.ndim != 1 ) {
            throw std::runtime_error("Number of dimensions must be one");
        }
        if( (bufa.shape[0] != bufb.shape[0]) ) {
            throw std::runtime_error("Input shapes must match");
        }
     // provide access to raw memory
     // because the Numpy arrays are mutable by default, py::array_t is mutable too.
     // Below we declare the raw C++ arrays for x and y as const to make their intent clear.
        double const *ptra = static_cast<double const *>(bufa.ptr);
        double const *ptrb = static_cast<double const *>(bufb.ptr);
    
     // compute the dot product and return the result:
        double d = 0.0;
        for (size_t i = 0; i < bufa.shape[0]; i++)
           d += ptra[i] * ptrb[i];
        return d;
    }
    
    // describe what goes in the module
    PYBIND11_MODULE(dotc, m) // `m` is a variable holding the module definition
                             // `dotc` is the module's name
    {// A module doc-string (optional):
        m.doc() = "C++ binary extension module `dotc`";
     // List the functions you want to expose:
     // m.def("exposed_name", function_pointer, "doc-string for the exposed function");
        m.def("dot", &dot, "Compute the dot product of two arrays.");
    }

Obviously the C++ source code is more involved than its Fortran equivalent in the
previous section. This is because f2py_ is a program performing clever
introspection into the Fortran source code, whereas pybind11_ is just a C++ template
library and as such it needs a little help from the user. This is, however, compensated
by the flexibility of Pybind11_.

We can now build the module:

.. code-block:: 

    micc2 build dotc
    [INFO] [ Building cpp module 'et_dot/dotc':
    [DEBUG]          [ > cmake -D PYTHON_EXECUTABLE=/Users/etijskens/.pyenv/versions/3.8.5/bin/python -D pybind11_DIR=/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/pybind11/share/cmake/pybind11 ..
    [DEBUG]              (stdout)
                           -- The CXX compiler identification is AppleClang 12.0.5.12050022
                           -- Detecting CXX compiler ABI info
                           -- Detecting CXX compiler ABI info - done
                           -- Check for working CXX compiler: /Library/Developer/CommandLineTools/usr/bin/c++ - skipped
                           -- Detecting CXX compile features
                           -- Detecting CXX compile features - done
                           pybind11_DIR : /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/pybind11/share/cmake/pybind11
                           -- Found PythonInterp: /Users/etijskens/.pyenv/versions/3.8.5/bin/python (found version "3.8.5") 
                           -- Found PythonLibs: /Users/etijskens/.pyenv/versions/3.8.5/lib/libpython3.8.a
                           -- Performing Test HAS_FLTO
                           -- Performing Test HAS_FLTO - Success
                           -- Performing Test HAS_FLTO_THIN
                           -- Performing Test HAS_FLTO_THIN - Success
                           -- Found pybind11: /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/pybind11/include (found version "2.6.2" )
                           -- Configuring done
                           -- Generating done
                           -- Build files have been written to: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build
    [DEBUG]          ] done.
    [DEBUG]          [ > make VERBOSE=1
    [DEBUG]              (stdout)
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -S/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc -B/Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build --check-build-system CMakeFiles/Makefile.cmake 0
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_progress_start /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build/CMakeFiles /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build//CMakeFiles/progress.marks
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/Makefile2 all
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/dotc.dir/build.make CMakeFiles/dotc.dir/depend
                           cd /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build && /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_depends "Unix Makefiles" /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build/CMakeFiles/dotc.dir/DependInfo.cmake --color=
                           /Library/Developer/CommandLineTools/usr/bin/make  -f CMakeFiles/dotc.dir/build.make CMakeFiles/dotc.dir/build
                           [ 50%] Building CXX object CMakeFiles/dotc.dir/dotc.cpp.o
                           /Library/Developer/CommandLineTools/usr/bin/c++ -Ddotc_EXPORTS -isystem /Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/pybind11/include -isystem /Users/etijskens/.pyenv/versions/3.8.5/include/python3.8 -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX11.3.sdk -fPIC -fvisibility=hidden -flto -std=gnu++11 -MD -MT CMakeFiles/dotc.dir/dotc.cpp.o -MF CMakeFiles/dotc.dir/dotc.cpp.o.d -o CMakeFiles/dotc.dir/dotc.cpp.o -c /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/dotc.cpp
                           [100%] Linking CXX shared module dotc.cpython-38-darwin.so
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_link_script CMakeFiles/dotc.dir/link.txt --verbose=1
                           /Library/Developer/CommandLineTools/usr/bin/c++  -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX11.3.sdk -bundle -Wl,-headerpad_max_install_names -Xlinker -undefined -Xlinker dynamic_lookup -flto -o dotc.cpython-38-darwin.so CMakeFiles/dotc.dir/dotc.cpp.o 
                           [100%] Built target dotc
                           /usr/local/Cellar/cmake/3.21.2/bin/cmake -E cmake_progress_start /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/_cmake_build/CMakeFiles 0
    [DEBUG]          ] done.
    [DEBUG]          [ > make install
    [DEBUG]              (stdout)
                           Consolidate compiler generated dependencies of target dotc
                           [100%] Built target dotc
                           Install the project...
                           -- Install configuration: ""
                           -- Installing: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc/../dotc.cpython-38-darwin.so
    [DEBUG]          ] done.
    [INFO] ] done.
    [INFO]           Binary extensions built successfully:
    [INFO]           - /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot/et_dot/dotc.cpython-38-darwin.so
    ['/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages', '/Users/etijskens/.local/lib/python3.8/site-packages']
    path_to_cmake_tools=/Users/etijskens/.pyenv/versions/3.8.5/lib/python3.8/site-packages/pybind11/share/cmake/pybind11
    

The ``build`` command produces quit a bit of output, though typically less that for a
Fortran binary extension module. If the source file does not have any syntax errors,
and the build did not experience any problems, the package directory :file:`et_dot`
will contain a binary extension module :file:`dotc.cpython-38-darwin.so`, along
with the previously built :file:`dotf.cpython-38-darwin.so`.

Here is some test code. It is almost exactly the same as that for the f90 module
:py:mod:`dotf`, except for the module name. Enter the test code in
:file:`ET-dot/tests/et_dot/dotc/test_dotc.py`:

.. code-block:: python

    import numpy as np
    import et_dot
    
    # create alias to dotc binary extension module:
    cpp = et_dot.dotc
    
    def test_dotc_aa():
        a = np.array([0, 1, 2, 3, 4], dtype=float)
        expected = np.dot(a, a)
        # call function dotc in the binary extension module:
        a_dot_a = cpp.dot(a, a)
        assert a_dot_a == expected

The test passes successfully. Obviously, you should also add the other tests we
created for the Python implementation. 

.. code-block:: 

    pytest tests/et_dot/dotc/test_dotc.py
    ============================= test session starts ==============================
    platform darwin -- Python 3.8.5, pytest-6.2.2, py-1.11.0, pluggy-0.13.1
    rootdir: /Users/etijskens/software/dev/workspace/et-micc2-tutorials-workspace-tmp/ET-dot
    collected 1 item
    
    tests/et_dot/dotc/test_dotc.py .                                         [100%]
    
    ============================== 1 passed in 0.78s ===============================
    

