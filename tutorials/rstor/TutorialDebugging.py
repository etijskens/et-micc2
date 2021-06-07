"""Build DEBUGGING.rst

"""
from et_rstor import *

def TutorialDebugging():

    doc = RstDocument('DEBUGGING', headings_numbered_from_level=2, is_default_document=True)
    with pickled.open(mode='r') as f:
        doc.heading_numbers = json.load(f)

    Include('../HYPERLINKS.rst')

    Heading('Debugging binary extensions', level=2)

    Paragraph(
        "Debugging is the process of executing a program step by step, in order to discover "
        "where and why it goes wrong. It is an indispensable step in software development. "
        "Although tests may tell you what part of your code fails, but the origin of the "
        "failure is not always clear."
    )
    Paragraph(
        "Graphical Debuggers as provided in IDEes, e.g. PyCharm, Eclipse_ + pydev_, Visual Studio, "
        "present a great user experience, but not all are capable of debugging mixed Python/C++/Fortran. "
        "See `here <https://wiki.python.org/moin/IntegratedDevelopmentEnvironments>`_ for more information."
    )
    List(
        [ "Pycharm_: only Python, but great user experience."
        , "eclipse: debugging binaries should be possible but not really mixed mode."
        , "Visual Studio: `Mixed language Python & C++ debugging with Python Tools for Visual Studio <https://www.youtube.com/watch?v=zEDFH1vMA24>_."
        ]
    )
    Paragraph(
        "For HPC environments there is also:"
    )
    List(
        [ "`Arm DDT <https://www.arm.com/products/development-tools/server-and-hpc/forge/ddt>`_"
        , "`TotalView HPC Debugging Software <https://totalview.io/products/totalview>`_"
        ]
    )
    Paragraph(
        "These are also capable debugging OpenMP (multi-threaded) and MPI applications "
        "(multi-process)."
    )

    Paragraph(
        "For Linux environments there is also a lightweight approach possible using gdb_ and "
        "pdb_. On MACOS gdb_ can be replaced by lldb_, which has very similar features, but "
        "different commands. (At the time of writing gdb_ for MACOS was broken). Here are two "
        "links describing the approach:"
    )
    List(
        [ "https://www.researchgate.net/figure/Debugging-both-C-extensions-and-Python-code-with-gdb-and-pdb_fig2_220307949"
        , "https://www.boost.org/doc/libs/1_76_0/libs/python/doc/html/faq/how_do_i_debug_my_python_extensi.html"
        ]
        , numbered=True
    )
    Paragraph(
        "The first link describes a fully mixed Python C++ approach, and works for Fortran as well. The"
        "second link, is semi-mixed. It expects you to enter the Python commands yourself, which may "
        "be tedious at times, but can be practical to explore the situation."
    )
    Paragraph(
        "We illustrate both strategies using a project foo with a C++ binary extension ``cxx``, and a "
        "Fortran binary extension ``fortran``. The code we are using is just the example code created "
        "by micc2_. "
    )
    CodeBlock(
        [ '> micc2 create foo --package'
        , '...'
        , '> micc2 add cxx --cpp'
        , '...'
        , '> micc2 add fortran --f90'
        , '...'
        , '> micc2 info'
        , 'Project foo located at /Users/etijskens/software/dev/workspace/foo'
        , '  package: foo'
        , '  version: 0.0.0'
        , '  structure: foo/__init__.py (Python package)'
        , '  contents:'
        , '    C++ module  cpp_cxx/cxx.cpp'
        , '    f90 module f90_fortran/fortran.f90'
        , '    f90 module f90_fortran/_cmake_build/Users/etijskens/software/dev/workspace/foo/foo/f90_fortran/fortran.f90'
        ]
    )

    Heading("Mixed Python/C++/Fortran debugging with gdb and pdb", level=3)

    Paragraph(
        "This is the approach of the first link above. We demonstrate it on a Mac, using lldb_ instead of gdb_. "
        "The commands are different for ``gdb`` and ``lldb``, but the strategy is exactly the same. First, "
        "start lldb_ with the Python executable you want to use. As I am using pyenv_ to manage differen python "
        "versions on my machine, the ``python`` on the PATH is only a wrapper for the the real Python executable, "
        "so I must specify the full path, because ``lldb`` expects a true executable."
    )
    CodeBlock(
        [ '> lldb ~/.pyenv/versions/3.8.5/bin/python'
        , '(lldb) target create "/Users/etijskens/.pyenv/versions/3.8.5/bin/python"'
        , 'Current executable set to \'/Users/etijskens/.pyenv/versions/3.8.5/bin/python\' (x86_64).'
        , '(lldb) target create "/Users/etijskens/.pyenv/versions/3.8.5/bin/python"'
        , '(lldb)'
        ]
    )
    """
(lldb) target create "/Users/etijskens/.pyenv/versions/3.8.5/bin/python"

(lldb)"""
if __name__ == '__main__':
    TutorialDebugging()
    print('-*# finished #*-')