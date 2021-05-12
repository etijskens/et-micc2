.. include:: ../HYPERLINKS.rst

So, the general advice is: use functions to return only variables of small size, like a
single number, or a tuple, maybe even a small fixed size array, but certainly not a
large array. If you have result variables of large size, compute them in place in
parameters with ``intent(inout)``. If there is no useful small variable to return,
use a subroutine instead of a function. Sometimes it is useful to have functions
return an error code, or the CPU time the computation used, while the result of the
computation is computed in a parameter with ``intent(inout)``, as below:

.. code-block:: fortran

    function add(a,b,sum,n)
      ! Compute the sum of arrays a and b and overwrite array sumab with the result
      ! Return the CPU time consumed in seconds.
        implicit none
        real*8 add ! return value
      !-------------------------------------------------
      ! Declare arguments
        integer*4              , intent(in)    :: n
        real*8   , dimension(n), intent(in)    :: a,b
        real*8   , dimension(n), intent(inout) :: sum
      !-------------------------------------------------
      ! declare local variables
        integer*4 :: i
        real*8 :: start, finish
      !-------------------------------------------------
      ! Compute the result
        call cpu_time(start)
          do i=1,n
            sum(i) = a(i) + b(i)
          end do
        call cpu_time(finish)
        add = finish-start
    end function add


Note that Python does not require you to store the return value of a function. The above
``add`` function might be called as:

.. code-block:: pycon

    >>> import numpy as np
    >>> import et_dot
    >>> a = np.array([1.,2.])
    >>> b = np.array([3.,4.])
    >>> sum = np.empty(len(a),dtype=float)
    >>> cputime = et_dot.dotf.add(a,b, sum)
    >>> print(cputime)
    5.000000000032756e-06
    >>> print(sum)
    [4. 6.]
    
