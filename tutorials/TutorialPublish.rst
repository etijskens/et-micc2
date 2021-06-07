.. include:: ../HYPERLINKS.rst

.. _publishing:

7. Publishing your code
=======================

By publising your code other users can easily reuse your code. Although a public
GitHub_ repository makes that possible, Python provides the Python Package Index
(PyPI_). Packages published on PyPI_ can be installed by anyone using pip_.

.. _publish-pypi:

7.1. Publishing to the Python Package Index
-------------------------------------------

Poetry_ provides really easy interface to publishing your code to the Python Package
Index (PyPI_). To install poetry see
https://python-poetry.org/docs/#installation. You must also create a PyPI_
account `here <https://pypi.org/account/register/>`_. Thento publish the
:file:`ET-dot` package, run this command in the project directory:this command in
the project directory, of:

.. code-block:: bash

    > poetry publish --build
    Creating virtualenv et-dot in /Users/etijskens/software/dev/workspace/Tutorials/ET-dot/.venv
    Building ET-dot (0.0.1)
      - Building sdist
      - Built ET-dot-0.0.1.tar.gz
      - Building wheel
      - Built ET_dot-0.0.1-py3-none-any.whl
    
    Publishing ET-dot (0.0.1) to PyPI
     - Uploading ET-dot-0.0.1.tar.gz 100%
     - Uploading ET_dot-0.0.1-py3-none-any.whl 100%

In order for your project to be publishable, it is necessary that the project name is
not already in use on PyPI_. As there are 100s of projects on PyPI_, it is wise to check
that. You can do this manually, but micc2_ also provides a ``--publish`` flag for the
``micc2 create`` command that verifies that the project name is still available on
PyPI_. If the name is already taken, the project will not be created and micc2_ will
suggest to choose another project name. See :ref:`project-name` for
recommendations of how to choose project names. If the name is not yet taken, it is wise
to publish the freshly created project right away (even without any useful
contents), to make sure that no one else can publish a project with the same name.

Note that a single version of a project can only be published once. If the
:file:`ET-dot` must be modified, e.g. to fix a bug, one must bump the version number
before it can be published again. Once a version is published it cannot be modified.

After the project is published, everyone can install the package in his current
Python environment as:

.. code-block:: bash

    > pip install et-foo
    ...

7.1.1. Publishing packages with binary extension modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Packages with binary extension modules are published in exactly the same way. That
is, perhaps surprisingly, as a Python-only project. When you ``pip install`` a
Micc2_ project, the package directory will end up in the :file:`site-packages`
directory of the Python environment in which you install. The source code
directories of the binary extensions modules are also installed with the package,
but without the binary extensions themselves. These must be compiled locally.
Micc2_ has added some machinery to automatically build the binary extensions from
the source code, as explained in detail at the end of section :ref:`building-f90`.
Obviously, this 'auto-build', can only succeed if the necessary tools are
available. In case of failure because of missing tools, micc2_ will tell you which
tools are missing.

7.2. Publishing your documentation on readthedocs.org
-----------------------------------------------------

Publishing your documentation to `Readthedocs <https://readthedocs.org>`_
relieves the users of your code from having to build documentation themselves.
Making it happen is very easy. First, make sure the git repository of your code is
pushed on Github_. Second, create a Readthedocs_ account if you do not already have
one. Then, go to your Readthedocs_ page, go to *your projects* and hit import
project. After filling in the fields, the documentation will be rebuild and
published automatically every time you push your code to the Github_ remote
repository.

.. note::

   Sphinx must be able to import your project in order to extract the documentation. If
   your codes depend on Python modules other than the standard library, this will fail
   and the documentation will not be built. You can add the necessary dependencies to
   :file:`<your-project>/docs/requirements.txt`.

