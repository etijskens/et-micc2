This file documents a python module built from C++ code with pybind11.
You should document the Python interfaces, *NOT* the C++ interfaces.

Module {{tmpl.import_lib}}
**************************

Module :py:mod:`{{tmpl.module_name}}` built from C++ code in :file:`{{tmpl.source_dir}}/{{tmpl.module_name}}.cpp`.

.. function:: add(x,y,z)
   :module: {{tmpl.import_lib}}
   
   Compute the sum of *x* and *y* and store the result in *z* (overwrite).

   :param x: 1D Numpy array with ``dtype=numpy.float64`` (input)
   :param y: 1D Numpy array with ``dtype=numpy.float64`` (input)
   :param z: 1D Numpy array with ``dtype=numpy.float64`` (output)
   