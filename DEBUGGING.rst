plan
----
https://www.researchgate.net/figure/Debugging-both-C-extensions-and-Python-code-with-gdb-and-pdb_fig2_220307949
https://www.boost.org/doc/libs/1_70_0/libs/python/doc/html/faq/how_do_i_debug_my_python_extensi.html

gdb on macos
------------

.. code-block::
   > brew install gdb

This helped me to get gdb signed:
https://sourceware.org/gdb/wiki/PermissionsDarwin

But it turns out that the gdb from homebrew is broken:
https://gist.github.com/mike-myers-tob/9a6013124bad7ff074d3297db2c98247
