.. include:: ../HYPERLINKS.rst

.. _data-types:

3.5. Data type issues
---------------------

When interfacing several programming languages data types require special care. We
already noted that although conversions are automatic if possible, they may be
costly. It is always more computationally efficient that the data types on both sides
(Python and respectively Fortran or C++) correspond. Here is a table with the most
relevant numeric data types in Python, Fortran and C++.


    ================  ============================  =========  ====================  
    data type         Numpy(np)/Python              Fortran    C++                   
    ================  ============================  =========  ====================  
    unsigned integer  np.uint32                     N/A        signed long int       
    unsigned integer  np.uint64                     N/A        signed long long int  
    signed integer    np.int32, int                 integer*4  signed long int       
    signed integer    np.int64                      integer*8  signed long long int  
    floating point    np.float32, np,single         real*4     float                 
    floating point    np.float64, np.double, float  real*8     double                
    complex           np.complex64                  complex*4  std::complex<float>   
    complex           np.complex128                 complex*8  std::complex<double>  
    ================  ============================  =========  ====================  

If there is automatic conversion between two data types in Python, e.g. from
``float32`` to ``float64`` the wrappers around our function will perform the
conversion automatically if needed. This happens both for Fortran and C++. However,
this comes with the cost of copying and converting, which is sometimes not
acceptable.

The result of a Fortran function and a C++ function in a binary extension module is
**always copied** back to the Python variable that will hold it. As copying large
data structures is detrimental to performance this shoud be avoided. The solution to
this problem is to write Fortran functions or subroutines and C++ functions that
accept the result variable as an argument and modify it in place, so that the copy
operaton is avoided. Consider this example of a Fortran subroutine that computes the
sum of two arrays.

.. code-block:: fortran

    subroutine add(a,b,sum,n)
      ! Compute the sum of arrays a and b and overwrite
      ! array sum with the result
        implicit none
      !-------------------------------------------------
      ! Declare arguments
        integer*4              , intent(in)    :: n
        real*8   , dimension(n), intent(in)    :: a,b
        real*8   , dimension(n), intent(inout) :: sum
      !-------------------------------------------------
      ! Declare local variables
        integer*4 :: i
      !-------------------------------------------------
      ! Compute the sum
        do i=1,n
            sum(i) = a(i) + b(i)
        end do
    end subroutine add


The crucial issue here is that the result array ``sumab`` is qualified as
``intent(inout)``, meaning that the ``add`` function has both read and write access
to it. This function would be called in Python like this:

Let us add this method to our :file:`dotf` binary extension module, just to
demonstrate its use.

.. code-block:: pycon

    >>> import numpy as np
    >>> import et_dot
    >>> a = np.array([1.,2.])
    >>> b = np.array([3.,4.])
    >>> sum = np.empty(len(a),dtype=float)
    >>> et_dot.dotf.add(a,b, sum)
    >>> print(sum)
    [4. 6.]
    
If ``add`` would have been qualified as as ``intent(in)``, as the input parameters
``a`` and ``b``, ``add`` would not be able to modify the ``sum`` array. On the other
hand, and rather surprisingly, qualifying it with ``intent(out)`` forces f2py_ to
consider the variable as a left hand side variable and define a wrapper that in Python
would be called like this:

.. code-block:: python

    sum = et_dot.dotf.add(a,b)

This obviously implies copying the contents of the result array to the Python
variable :file:`sum`, which, as said, may be prohibitively expensive.

