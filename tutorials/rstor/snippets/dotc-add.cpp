#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

void
add ( py::array_t<double> a
    , py::array_t<double> b
    , py::array_t<double> sum
    )
{// request buffer description of the arguments
    auto buf_a = a.request()
       , buf_b = b.request()
       , buf_sum = sum.request()
       ;
    if( buf_a.ndim != 1 || buf_b.ndim != 1 || buf_sum.ndim != 1 )
        throw std::runtime_error("Number of dimensions must be one");

    if( (buf_a.shape[0] != buf_b.shape[0]) || (buf_a.shape[0] != buf_sum.shape[0]) )
        throw std::runtime_error("Input shapes must match");

 // because the Numpy arrays are mutable by default, py::array_t is mutable too.
 // Below we declare the raw C++ arrays for a and b as const to make their intent clear.
    double const *ptr_a   = static_cast<double const *>(buf_a.ptr);
    double const *ptr_b   = static_cast<double const *>(buf_b.ptr);
    double       *ptr_sum = static_cast<double       *>(buf_sum.ptr);

    for (size_t i = 0; i < buf_a.shape[0]; i++)
        ptr_sum[i] = ptr_a[i] + ptr_b[i];
}

PYBIND11_MODULE(dotc, m)
{  m.doc() = "dotc binary extension module"; // optional module docstring
   m.def("add", &add, "compute the sum of two arrays.");
}
