**********
Change log
**********

v2.0.0
------
Prior to v2 micc-build and micc were added as a dependency of every micc project with binary
extensions. As a consequence all their subdependencies were added too. Amongst others:

* numpy
* pybind11
* sphinx
* pytest
* sphinx-click
* sphinx-rt-theme
* ...

When creating a virtual environment these dependencies put the file systems of the VSC clusters
pressure.

the idea is to put all dependencies we need in the user's site-packages.

* ``python -m pip install sphinx-rtd-theme (also installs sphinx)``
* ``python -m pip install sphinx-click (also installs click)``
* ``python -m pip install numpy``
* ``python -m pip install pybind11``
* ``python -m pip install pytest``
* ``python -m pip install poetry``
* ``python -m pip install micc2``

This duplicates all dependencies only once for each python version that the user
needs, which is much better than once per project. Also when working on the cluster,
even if the user creates his project on $VSC_SCRATCH instead of on $VSC_DATA the pressure
on the file system is much less.