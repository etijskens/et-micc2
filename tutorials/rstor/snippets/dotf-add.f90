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
