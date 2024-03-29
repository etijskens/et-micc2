.. include:: ../HYPERLINKS.rst

Can I use Anaconda Python distributions?
----------------------------------------
Yes, but installing your own conda distribution is not recommended on VSC clusters because it uses a lot
of disk space. If you cannot avoid it, install on the data file system.

Can I use micc2_ on the (VSC) clusters?
---------------------------------------
Yes, see :ref:`VSC-cluster-installation`.

IDEs and editors
----------------
I have been using different IDEs over time:

* eclipse_ + pydev_: steep learning curve, because of limited documentation. works well as a
  remote editor. no mixed language debugging. cross platform.
* PyCharm_ (CE): great user experience for Python only debugging, remote development only in
  professional edition. cross platform.
* Visual_Studio_Code_: local and remote editing, mixed language debugging Python/C++/Fortran.
  remote terminal allowing remote mixed language debugging. cross platform.

Currently, I consider Visual Studio Code as the most complete IDE for mixed language development for HPC environments.
In addition, it is free and open source. See also `Modern Python developer's toolkit <https://pycon.switowski.com/>`_.

Editors such as SublimeText and Atoms, or vim are useful too, but provide no integrated debugging.