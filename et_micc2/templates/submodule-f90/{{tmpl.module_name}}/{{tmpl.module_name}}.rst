This file documents a python module built from Fortran code with f2py.
You should document the Python interfaces, *NOT* the Fortran interfaces.

Module {{tmpl.import_lib}}
*************************

Module :py:mod:`{{tmpl.module_name}}` built from fortran code in :file:`{{tmpl.source_dir}}/{{tmpl.module_name}}.f90`.

.. function:: add(x,y,z)
   :module: {{tmpl.package_name}}.{{tmpl.module_name}}

   Compute the sum of *x* and *y* and store the result in *z* (overwrite).

   :param x: 1D Numpy array with ``dtype=numpy.float64`` (input)
   :param y: 1D Numpy array with ``dtype=numpy.float64`` (input)
   :param z: 1D Numpy array with ``dtype=numpy.float64`` (output)
