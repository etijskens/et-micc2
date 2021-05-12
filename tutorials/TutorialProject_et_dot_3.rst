.. include:: ../HYPERLINKS.rst

.. note::

   The Pybind11 wrappers automatically apply the same conversions as the F2py
   wrappers. Here is an example where the input arrays are a plain Python ``list``
   containing ``int`` values. The wrapper converts them on the fly into a contiguous
   array of ``float``valuwa (which correspond to C++'s ``double``) and returns a
   ``float``:

.. code-block:: pycon

    >>> import et_dot
    >>> print(et_dot.dotc.dot([1,2],[3,4]))
    11.0
    
This time, however, there is no warning that the wrapper converted or copied. As
converting and copying of large is time consuming, this may incur a non-negligable
cost on your application, Moreover, if the arrays are overwritten in the C++ code and
serve for output, the result will not be copied back, and will be lost. This will result
in a bug in the client code, as it will continue its execution with the original values. 

.. _control-build-cpp:

3.3.1. Controlling the build
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The build parameters for our C++ binary extension module are detailed in the file
:file:`et_dot/cpp_dotc/CMakeLists.txt`, just as in the f90 case. It contains
significantly less boilerplate code (which you should not need to touch) and
provides the same functionality. Here is the section of
:file:`et_dot/cpp_dotc/CMakeLists.txt` that you might want to adjust to your
needs:

.. code-block:: 

    ...                                                         # (boilerplate code omitted for clarity)
    ####################################################################################################
    ######################################################################### Customization section ####
    # set compiler:
    # set(CMAKE_CXX_COMPILER path/to/executable)
    # Set build type:
    # set(CMAKE_BUILD_TYPE DEBUG | MINSIZEREL | RELEASE | RELWITHDEBINFO)
    # Add compiler options:
    # set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} <additional C++ compiler options>")
    # Request a specific C++ standard:
    # set(CMAKE_CXX_STANDARD 17)
    # Add preprocessor macro definitions:
    # add_compile_definitions(
    #     OPENFOAM=1912                     # set value
    #     WM_LABEL_SIZE=$ENV{WM_LABEL_SIZE} # set value from environment variable
    #     WM_DP                             # just define the macro
    # )
    # Add include directories
    #include_directories(
    #     path/to/dir1
    #     path/to/dir2
    # )
    # Add link directories
    # link_directories(
    #     path/to/dir1
    # )
    # Add link libraries (lib1 -> liblib1.so)
    # link_libraries(
    #     lib1
    #     lib2
    # )
    ####################################################################################################
    ...                                                         # (boilerplate code omitted for clarity)

