.. include:: ../HYPERLINKS.rst

Micc2_ can be installed in different ways on your system.
Here is a simple decision scheme:

* if your OS is MACOS or Linux:

  * If your system is your own desktop or laptop, go to :ref:`desktop installation`
  * If your system is a VSC HPC cluster, go to :ref:`VSC cluster installation`.
    There are only a few important differences with the desktop installation.
    Installation on other HPC clusters is problably quite similar.

* If your OS is Windows, go to :ref:`windows-options`. Micc2_ was initially developed
  for HPC purposes. As most HPC clusters have a Linux OS, Micc2_ was developed for Linux,
  and, by extension, MACOS. However, many HPC users are running Windows on their desktop,
  so after Micc2_ settled, (some) support for Windows was added.


.. _desktop installation:

Installation on your desktop or laptop
--------------------------------------
The most practical way to install micc2_ on your desktop or laptop is ::

        > python -m pip install [--user] et-micc2

.. note:: If you have different Python versions, you need to do this for each Python
    version in which you need access to micc2_.

.. note:: If the current python is located in the system directories, and you do not
    have root access, the ``--user`` flag is necessary. Otherwise, not, but it is
    nevertheless wise to separate your "additions" from the system installation, in
    case you screw up.

Depending on which micc2_ functionality you need, micc2_ depends on other tools, which
are not automatically installed when installing micc2_. Micc2_ will warn you if you need
to install them:

  * Micc2_ sets up *version control* using git_. If you want another VCS, you must do that
    manually. If git_ is available, the command ``micc create`` will add a local git
    repository for your project. If gh_ is also available and you have added a personal
    access token for your github_ account, the ``micc create`` command can also automatically
    creeate a remote github_ repository (public by default) for your project. Git_ and gh_
    are usually installed system-wide.

  * Building *binary extensions from Fortran* requires CMake_ and numpy_. CMake_ can be
    installed system-wide, but also using pip_::

        > python -m pip install [--user] cmake

    If you have different Python versions, it is recommended to do a system-wide installation.
    Numpy_ is installed with pip_::

        > python -m pip install [--user] numpy

    You also need a Fortran and a C compiler on your PATH.

  * Building *binary extensions from C++* requires CMake_ and pybind11_. The latter is
    installed as::

        > python -m pip install [--user] pybind11

    You also need a C++ compiler on your PATH.

  * Tests and unit-tests can be done with pytest_. Install as::

        > python -m pip install [--user] pytest

  * Building documentation requires sphinx_ and a suitable html theme, typically sphinx_rtd_theme_::

        > python -m pip install [--user] sphinx
        > python -m pip install [--user] sphinx-rtd-theme

    If you have want to extract documentation from command line applications (CLIs) based on
    click_, you also need sphinx_click_::

        > python -m pip install [--user] sphinx-click

  * Publishing your project to PyPI_ is easily achieved with poetry_(``poetry publish --build``).
    We recommend to install it separately for each Python version::

        > python -m pip install [--user] poetry

.. _VSC cluster installation:

Installation on a HPC cluster
-----------------------------
On typical HPC clusters (such as those of the VSC) application software must me made
available by loading cluster *modules*. Even if the operating system of the login nodes
and compute nodes posses versions of the above tools, they are typically not the most
recent ones and have not been compiled for optimal performance on HPC systems, and you must
load cluster modules for:

  * Python
  * git
  * gh
  * CMake
  * numpy
  * pytest

Some cluster modules expose several tools in one go. E.g., on the VSC cluster Leibniz
one can use::

    > module load Python
    > module load buildtools
    > module load gh
    > module list
    Currently Loaded Modules:
      1) leibniz/supported              6) Tcl/8.6.10-intel-2020a       11) METIS/5.1.0-intel-2020a-i32-fp64
      2) GCCcore/9.3.0                  7) X11/2020a-GCCcore-9.3.0      12) SuiteSparse/5.7.1-intel-2020a-METIS-5.1.0
      3) binutils/2.34-GCCcore-9.3.0    8) Tk/8.6.10-intel-2020a        13) Python/3.8.3-intel-2020a
      4) intel/2020a                    9) SQLite/3.31.1-intel-2020a    14) buildtools/2020a
      5) baselibs/2020a-GCCcore-9.3.0  10) HDF5/1.10.6-intel-2020a-MPI  15) gh/1.8.0

Together with Python 3.8.3, this gives us most of the tools and packages micc2_ needs::

    > git --version
    git version 2.26.0

    > gh --version
    gh version 1.8.0 (2021-03-30)
    https://github.com/cli/cli/releases/tag/v1.8.0

    > cmake --version
    cmake version 3.17.0
    CMake suite maintained and supported by Kitware (kitware.com/cmake).

    > pytest --version
    This is pytest version 5.4.1

    > python
    Python 3.8.3 (default, May 27 2020, 11:32:18)
    [GCC Intel(R) C++ gcc 9.3 mode] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import numpy
    >>> numpy.__version__
    '1.18.3'

Some packages are missing, however, notably the sphinx_ related ones, but for a reason:
it is strongly discouraged to use HPC clusters for building documentation. Building
documentation is not computationally intensive enough to engage a supercomputer. In is
on the contrary I/O intensive and may put the cluster's file system under stress.
So do not install any sphinx_ related packages on your cluster. Documentation should be
built on a desktop/laptop system.

Poetry_ is also missing. As long as the virtual environments created by poetry_
have problems with honoring the ``--system-site-packages`` flag, we do not recommend
poetry_ for use on the cluster. Publishing can be done in a desktop environment, just
like building documentation.

The other tools can just be installed as in :ref:`desktop installation`, but the
``--user`` flag **must** be added, since you have no privileges for writing to the cluster
system directories. So::

    > python -m pip install --user et-micc2
    > python -m pip install --user pybind11

What about virtual environments?
--------------------------------
Virtual environments are extremely usefull to isolate the dependencies of different
projects. If the your project has dependencies which are incompatible with those of
micc2_, you can separate them into two virtual environments, one for running
micc2_ and managing the project, and one for the project itself and its dependencies.
Both environments can even be based on different Python versions.

You create a virtual environment like this::

    > python -m venv venv-name

This creates a directory ``venv-name`` in the current directory containing a complete
virtual Python environment based on your current ``python`` executable. It provides just
a bare Python installation, no site packages. If you also want the system site packages
to be available in the virtual environment, specify the ``--system-site-packages`` flag::

    > python -m venv venv-name --system-site-packages

.. note:: The ``--system-site-packages`` flag is highly recommended when working on the
    cluster because it enables Python Packages which are built for optimal performance
    on HPC systems, e.g. numpy, scipy, hdf5py, ...  Installing these packages yourself,
    will consume a lot of your disk space and yield suboptimal performance.

.. note:: ``venv`` uses symbolic links as much as possible, as to use disk space efficiently.
    If symbolic links are not the default for your system, add the ``--symlinks`` flag

A virtual environment is activated as::

    > source venv-name/bin/activate
    (venv-name) >

Note how the prompt is modified, as to show the active virtual environment.

.. note:: Do not use the ``--user`` flag when installing in a virtual environment.

To deactivate an activated virtual environment, run::

    (venv-name) > deactivate
    >

The prompt returns back to normal. If you do not need your venv anymore, you can
delete it like any other directory::

    > rm -rf venv_name

Now you can use the virtual environment, and install packages in it without i
mpacting anything else. E.g. a micc2_ virtual environment could be created in
a terminal as::

    > python -m venv venv-micc2 --system-site-packages
    > source venv-micc2/bin/activate
    (venv-micc2) > python -m pip install et-micc2
    (venv-micc2) > python -m pip install pybind11
    (venv-micc2) >

Here, you issue the project management commands, add components, modify version,
build binary extensions, etc. In another terminal you create a virtual environment
for the project you are working on, say project ``FOO``. Typically, it is created
inside the ``FOO`` project directory itself:

    > cd path/to/FOO
    > python -m venv .venv-FOO --system-site-packages
    > source .venv-FOO/bin/activate
    (.venv-FOO) >

Note, that the Python version to create the virtual and need not be the same as
that of the micc2_ environment.

So far, this virtual environment ``.venv-FOO`` does not know about ``FOO``. We must
still install ``FOO``. Typically, during development, you want an editable install,
so that any changes to``FOO``'s source code are instantly visible in the virtual
environment. Micc2_ provides a script for that purpose::

    (.venv-FOO) > python ~/.et_micc2/scripts/install-e.py
    Create editable install of project `FOO` in current Python environment (=/Users/etijskens/.pyenv/versions/3.8.5)?
    Proceed (yes/no)? y

    Proceeding ...
    > /Users/etijskens/.pyenv/versions/3.8.5/bin/python -m pip install --user .
    Processing /Users/etijskens/software/dev/workspace/FOO
      Installing build dependencies ... done
      Getting requirements to build wheel ... done
        Preparing wheel metadata ... done
    Building wheels for collected packages: foo
      Building wheel for foo (PEP 517) ... done
      Created wheel for foo: filename=FOO-0.0.0-py3-none-any.whl size=10686 sha256=153875968adc059610dba8cd1184fcd8ba93b658f67039fa6af8d02b07127a13
      Stored in directory: /private/var/folders/rt/7h5lk6c955db20y1rzf1rjz00000gn/T/pip-ephem-wheel-cache-x03e7s9q/wheels/a9/a4/e2/b61066293a36081a4330481401f731ee167914546c9f637bff
    Successfully built foo
    Installing collected packages: foo
      Attempting uninstall: foo
        Found existing installation: foo 0.0.0
        Uninstalling foo-0.0.0:
          Successfully uninstalled foo-0.0.0
    Successfully installed foo-0.0.0
    WARNING: You are using pip version 21.0.1; however, version 21.1 is available.
    You should consider upgrading via the '/Users/etijskens/.pyenv/versions/3.8.5/bin/python -m pip install --upgrade pip' command.
    Package `foo` installed at `/Users/etijskens/.local/lib/python3.8/site-packages`.

    Removing package: /Users/etijskens/.local/lib/python3.8/site-packages/foo
    Replacing package with symbolic link: /Users/etijskens/software/dev/workspace/FOO/foo
    Editable install of FOO is ready.
    (.venv-FOO) >

Now, the package ``FOO`` is available in ``.venv-FOO`` and any code changes to ``FOO``'s
source code are immediately visible in ``.venv-FOO``.

.. note:: Micc2 projects lack a ``setup.py`` file, and consequently ``pip install -e path/to/FOO``
    will fail. The ``install-e.py`` script provides a work around for this. For non-editable
    installs ``pip install path/to/FOO`` works flawless.

Note that this works exactly the same way on the cluster, provided you load the
appropriate cluster modules to expose the cluster tools that you need, prior to
creating and activating the virtual environments.

.. _windows_options:

Windows
-------
If you want to use Micc2_ on Windows, you have a few options,
most of which are incompletely tested. 

Native Windows Python environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Native Python on Windows is compiled with the C/C++ compilers distributed with
Visual Studio. Micc2_ works nicely in this environment, and can build binary
extensions from C++ code using the Visual Studio compilers (You need the
*Build Tools for Visual Studio 2019*). According to
`this article <https://stackoverflow.com/questions/25671354/using-f2py-with-windows-x64-and-intel-fortran>`_
it should also be possible to build binary extensions from Fortran code when
you install the Intel Fortran compiler. Unfortunately, I cannot test it because
I do not have a Windows machine, and my Macbook has not enough disk space for
installing the complete Intel OneAPI Base Toolkit and Intel OneAPI HPC toolkit ...

This is probably the most Windows-like approach possible. Note that PyCharm_
is available for Windows too.

WSL-2
^^^^^
Modern Windows versions are equiped with *Windows Subsystem for Linux*, a
compatibility layer for running Linux binary executables (in ELF format)
natively on Windows 10. It provides you with a (virtual) Linux terminal
which should be able to run all the tools just as in a MACOS or Linux
terminal. It should be possible to build binary extension from C++ and
Fortran code using the Gnu Compiler Collection (GCC).

Cygwin
^^^^^^
Cygwin_ is a large collection of GNU and Open Source tools which provide
functionality similar to a Linux distribution on Windows. It provides all
the necessary tools for building binary extension from C++ and Fortran code
using the Gnu Compiler Collection (GCC).


.. _micc2-setup:

First time Micc2 setup
----------------------

When you run Micc2_ for the first time, it will complain that it has not been set
up yet, and that you need to run ``micc2 setup``. In order to facilitate your project
management as much as possible,  Micc2_ needs to know some personal data such as your
name, e-mail address, github account, ...  If you do not have a github account yet,
create a github account at https://github.com>/join/.

Then, run::

    > micc2 setup

The dialogue that follows asks for your full name, your e-mail address, your
github username, a default html theme for Sphinx_ documentation, and a default
license. For the last two questions you can select a default answer by just hitting
``enter``. Finally, Micc2_ shows you the chosen preferences and asks for permission
to save the results. The dialogue goes like this::

    Enter your full name
    Enter `^^` to exit.
    >: John Doe

    Enter your e-mail address
    Enter `^^` to exit.
    >: john.doe@example.com

    Enter your github username (leave empty if you do not have one,
      or create one first at https://github.com/join). Default = []
    Enter `^^` to exit.
    >: jdoe

    Enter Html theme for sphinx documentation. Default = [sphinx_rtd_theme]
    Enter `^^` to exit.
    >:

    Enter the default software license [GNU General Public License v3]
    Choose between:
      0: GNU General Public License v3 (default)
      1: MIT license
      2: BSD license
      3: ISC license
      4: Apache Software License 2.0
      5: Not open source
    Enter `^^` to exit.
    >:
    >: GNU General Public License v3
    These preferences are saved to /Users/etijskens/.micc2/micc2.cfg:
    {
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "github_username": "jdoe",
      "sphinx_html_theme": "sphinx_rtd_theme",
      "software_license": "GNU General Public License v3",
      "version": "0.0.0",
      "github_repo": "{{cookiecutter.project_name}}",
      "git_default_branch": "main",
      "minimal_python_version": "3.7",
      "py": "py"
    }
    Continue? yes/no >:
    Preferences saved to /Users/etijskens/.micc2/micc2.cfg.

Micc2_ uses your name and e-mail address to configure git.

Finally, if you want to be able to automatically create remote github repositories,
you need also a personal access token for your github account. Follow
`these instructions <https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token>`_
At point 7 check at least these boxes:

    * repo
    * read:org

At point 9 copy the token to the clipboard and paste it in file
:file:`~/.micc2/<your-github-username>.pat`, like this::

    > echo <paste> > ~/.micc2/<your-github-username>.pat

Here <paste> stands for your OS's keyboard combination for pasting in the terminal.
( Typically: Linux: shift+ctrl+v, MACOS: command+v, Windows: ctrl+v).
