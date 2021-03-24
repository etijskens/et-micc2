.. highlight:: shell

.. _micc: https://micc.readthedocs.io
.. _micc-build: https://micc.readthedocs.io

************
Installation
************

It is recommended to install micc_ system-wide with `pipx <https://github.com/pipxproject/pipx>`_.

.. code-block:: console

    > pipx install et-micc2
    
Upgrading to a newer version is done as:

.. code-block:: console

    > pipx upgrade et-micc2

To install micc in your current Python environment, run this command in your terminal:

.. code-block:: console

    > pip install et-micc2

Debugging ``micc2``
-------------------
To test/debug micc_ on a specific project, run:

.. code-block:: console

    (.venv)> path/to/et-micc2/symlink-micc.sh

As indicated, the projects virtual environmentmust be activated. The current working
directory is immaterial, though. This command replaces the package folders ``et_micc2``
in the projects virtual environment's ``site-packages`` folder
with a symbolic link to the project module directories ``et-micc2/et_micc2``,
so that any changes in those are immediately visible
in the project your are working on.

Productivity tip: put a symbolic link to symlink-micc.sh somewhere on the path.