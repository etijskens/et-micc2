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
