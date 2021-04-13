*****
Micc2
*****

.. image:: https://img.shields.io/pypi/v/micc2.svg
        :target: https://pypi.python.org/pypi/micc2

.. image:: https://img.shields.io/travis/etijskens/micc2.svg
        :target: https://travis-ci.org/etijskens/micc2

.. image:: https://readthedocs.org/projects/micc2/badge/?version=latest
        :target: https://micc2.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

`Micc2_ <https://github.com/etijskens/et-micc2>`_ is a Python project manager: it helps
you organize your Python project from simple single file modules to fully fledged 
Python packages containing modules, sub-modules, apps and binary extension modules 
written in Fortran or C++. Micc2_ organizes your project in a way that is considered good
practice by a large part of the Python community. 

* Micc2_ helps you create new projects. You can start small with a simple one-file 
  package and add material as you go, such as:
  
  * Python **sub-modules** and **sub-packages**,
  * **applications**, also known as command line interfaces (CLIs). 
  * **binary extension modules** written in C++ and Fortran. Boiler plate code is 
    automatically added as to build these binary extension with having to go through
    al the details. This is, in fact, the foremost reason that got me started on this
    project: For *High Performance Python* it is essential to rewrite slow and 
    time consuming parts of a Python script or module in a language that is made 
    for High Performance Computing. As figuring out how that can be done, requires 
    quite some effort, Micc2_ was made to automate this part while maintaining the 
    flexibility. 
  * Micc2_ adds typically files containing example code that shows you how to add your
    own functionality.
    
* You can automatically **extract documentation** from the doc-strings of your files,
  and build html documentation that you can consult in your browser, or a .pdf 
  documentation file.
* With a little extra effort the generated html **documentation is automatically published** 
  to `readthedocs <https://readthedocs.org>`_.
* Micc2_ helps you with **version management and control**.
* Micc2_ helps you with **testing** your code.
* Micc2_ helps you with **publishing** your code to e.g. `PyPI <https://pypi.org>`_, so
  that you colleagues can use your code by simply running::

    > pip install your_nifty_package

Credits
-------
Micc2_ does not do all of this by itself. For many things it relies on other strong 
open source tools. Here is a list of tools micc2_ is using or cooperating with happily:

*   `Pyenv <https://github.com/pyenv/pyenv>`_: management of different Python versions on your desktop.
*   `Poetry <https://python-poetry.org>`_ for packaging and publishing.
*   `Git <https://www.git-scm.com/>`_ for version control.
*   `Pytest <https://www.git-scm.com/>`_ for testing your code.
*   `Sphinx <http://www.sphinx-doc.org/>`_ to extract documentation from your project's
    doc-strings.
*   `CMake <https://cmake.org>`_ is used for building binary extension modules written
    in C++ and Fortran.
*   `F2py <https://docs.scipy.org/doc/numpy/f2py/>`_ for transforming modern Fortran code
    into performant binary extension modules interfacing nicely with numpy arrays.
*   `Pybind11 <https://pybind11.readthedocs.io/en/stable/>`_ as the glue between C++ source
    code and performant binary extension modules, also interfacing nicely with numpy arrays.

Roadmap
=======
These features are still on our wish list:

* Contininous integtration (CI)
* Code style, e.g. `flake8 <http://flake8.pycqa.org/en/latest/>`_ or `black <https://github.com/psf/black>`_
* Profiling
* Gui for debugging C++/Fortran binary extensions
* Micc2 projects on Windows (So far, only support on Linux and MacOS).

