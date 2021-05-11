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
type ``float``, which correspond to Fortran's ``real*8``.

