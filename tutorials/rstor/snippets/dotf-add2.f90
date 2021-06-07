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
