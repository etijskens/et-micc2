.. include:: ../HYPERLINKS.rst

.. _document-binary-extensions:

3.6. Documenting binary extension modules
-----------------------------------------

For Python modules the documentation is automatically extracted from the
doc-strings in the module. However, when it comes to documenting binary extension
modules, this does not seem a good option. Ideally, the source files
:file:`ET-dot/et_dot/f90_dotf/dotf.f90` and
:file:`ET-dot/et_dot/cpp_dotc/dotc.cpp` should document the Fortran functions
and subroutines, and C++ functions, respectively, rather than the Python
interface. Yet, from the perspective of ET-dot being a Python project, the user is
only interested in the documentation of the Python interface to those functions and
subroutines. Therefore, Micc2_ requires you to document the Python interface in
separate :file:`.rst` files:

* :file:`ET-dot/et_dot/f90_dotf/dotf.rst`

* :file:`ET-dot/et_dot/cpp_dotc/dotc.rst`

their contents could look like this: for
:file:`ET-dot/et_dot/f90_dotf/dotf.rst`:

.. code-block:: rst

    Module et_dot.dotf
    ******************
    
    Module (binary extension) :py:mod:`dotf`, built from fortran source.
    
    .. function:: dot(a,b)
       :module: et_dot.dotf
    
       Compute the dot product of ``a`` and ``b``.
    
       :param a: 1D Numpy array with ``dtype=float``
       :param b: 1D Numpy array with ``dtype=float``
       :returns: the dot product of ``a`` and ``b``
       :rtype: ``float``

and for :file:`ET-dot/et_dot/cpp_dotc/dotc.rst`:

.. code-block:: rst

    Module et_dot.dotc
    ******************
    
    Module (binary extension) :py:mod:`dotc`, built from C++ source.
    
    .. function:: dot(a,b)
       :module: et_dot.dotc
    
       Compute the dot product of ``a`` and ``b``.
    
       :param a: 1D Numpy array with ``dtype=float``
       :param b: 1D Numpy array with ``dtype=float``
       :returns: the dot product of ``a`` and ``b``
       :rtype: ``float``

The (html) documentation is build as always:

.. code-block:: 

    micc2 doc
    [INFO]           [ > make html
    [INFO]               (stdout)
                            Running Sphinx v3.5.3
                            making output directory... done
                            WARNING: html_static_path entry '_static' does not exist
                            building [mo]: targets for 0 po files that are out of date
                            building [html]: targets for 7 source files that are out of date
                            updating environment: [new config] 7 added, 0 changed, 0 removed
                            reading sources... [ 14%] api
                            reading sources... [ 28%] apps
                            reading sources... [ 42%] authors
                            reading sources... [ 57%] changelog
                            reading sources... [ 71%] index
                            reading sources... [ 85%] installation
                            reading sources... [100%] readme
                            
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/changelog.rst:1: WARNING: Problems with "include" directive path:
                            InputError: [Errno 2] No such file or directory: '../HISTORY.rst'.
                            looking for now-outdated files... none found
                            pickling environment... done
                            checking consistency... /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/apps.rst: WARNING: document isn't included in any toctree
                            done
                            preparing documents... done
                            writing output... [ 14%] api
                            writing output... [ 28%] apps
                            writing output... [ 42%] authors
                            writing output... [ 57%] changelog
                            writing output... [ 71%] index
                            writing output... [ 85%] installation
                            writing output... [100%] readme
                            
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            generating indices... genindex /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            py-modindex /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            done
                            highlighting module code... [ 50%] et_dot
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            highlighting module code... [100%] et_dot.dotc
                            
                            /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            writing additional pages... search /Users/etijskens/software/dev/workspace/tutorials-workspace-tmp/ET-dot/docs/index.rst:5: WARNING: toctree contains reference to document 'changelog' that doesn't have a title: no link will be generated
                            done
                            copying static files... done
                            copying extra files... done
                            dumping search index in English (code: en)... done
                            dumping object inventory... done
                            build succeeded, 16 warnings.
                            
                            The HTML pages are in _build/html.
    [INFO]           ] done.
    

As the output shows, the documentation is found in your project directory in
:file:`docs/_build/html/index.html`. It can be opened in your favorite browser.

.. code-block:: 

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

.. code-block:: 

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


