.. include:: ../HYPERLINKS.rst

.. _python-submodules:

4. Adding Python submodules
===========================

Adding binary extension (sub)module is important for adding implementations in
Fortran or C++ for performance reasons. For larger projects it is sometimes
practical to be able to organize your Python code in different files, e.g. one file for
each Python class. Micc2_ allows your to add Python submodules to your project. These
can have a module or a package stucture. This command adds a module :file:`foo.py` to
your project:

.. code-block:: 

    micc2 add foo --py
    [INFO]           [ Adding python module foo.py to project ET-dot.
    [INFO]               - python source in    ET-dot/et_dot/foo.py.
    [INFO]               - Python test code in ET-dot/tests/test_foo.py.
    [INFO]           ] done.
    

As the output shows, it creates a file :file:`foo.py` in the package directory
:file:`et_dot` of our :file:`ET-dot` project. In this file you can add all your `foo`
related code. Micc2_ ensures that this submodule is automatically imported in
:file:`et_dot`:

.. code-block:: 

    # In file `et_dot/__init__`:
    # This statement is added by Micc2_
    import et_dot.foo
    # Using method `foo_fun` from submodule `foo.py`:
    et_dot.foo.foo_fun()

