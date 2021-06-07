import sys

from helpers import *
from et_rstor import *


def TutorialVersionManagement():

    wsfoo = workspace/'foo'
    if (wsfoo).exists():
        shutil.rmtree(wsfoo)

    doc = RstDocument('TutorialVersionManagement', headings_numbered_from_level=2, is_default_document=True)
    doc.heading_numbers[2] = 5

    Include('../HYPERLINKS.rst')

    Heading('Version management', level=2, crosslink='version-management')

    Paragraph(
        "Version numbers are practical, even for a small software project used "
        "only by yourself. For larger projects, certainly when other users start "
        "using them, they become indispensable. When assigning a version number "
        "to a project, we highly recommend to follow the guidelines of "
        "`Semantic Versioning 2.0 <https://semver.org>`_. Such a version number "
        "consists of ``Major.minor.patch``. According to semantic versioning you "
        "should increment the:"
    )
    List(
        [ '``Major`` version when you make incompatible API changes,'
        , '``minor`` version when you add functionality in a backwards compatible manner, and'
        , '``patch`` version when you make backwards compatible bug fixes.'
        ]
    )
    Paragraph(
        "When Micc2_ creates a project, it puts a ``__version__`` string with value "
        "``'0.0.0'`` in the top level Python module of the project. So, users can access "
        "a Micc2_ package's version as ``package_name.__version__``. The version string "
        "is also encoded in the :file:`pyproject.toml` file. "
    )
    Note(
        "Although the ``__version__`` string approach did not make it as the Python "
        "standard approach for encoding versions strings (see "
        "`PEP 396 <https://www.python.org/dev/peps/pep-0396>`_), Micc2_ will still "
        "support it for some time because the accepted approach relies on the standard "
        "library package :file:`importlib.metadata`, which is only available for Python "
        "versions 3.8 and higher."
    )
    Paragraph(
        "The ``micc2 version`` command allows you to modify the version string consistently "
        "in a project. The most common way of modifying a project's version string "
        "is to 'bump' one of the version components, Major, minor, or patch. This implies "
        "incrementing the component by 1, and setting all the lower components to 0. This is "
        "illustrated below. Suppose we are the project director of package :file:`foo`:"
    )
    CodeBlock(
        'micc2 create foo --no-git'
        , execute=True, cwd=workspace, hide=True
    )
    CodeBlock(
        [ 'micc2 info'
        , 'micc2 version'
        , 'micc2 version --patch'
        , 'micc2 version --minor'
        , 'micc2 version --patch'
        , 'micc2 version --major'
        ]
        , execute=True, cwd=workspace/'foo'
    )
    Paragraph(
        "Without arguments the ``micc2 version`` command just shows the current version. "
        "Furthermore, the flags ``--patch``, ``--minor``, and ``--major`` can be abbreviated "
        "as ``-p``, ``-m`` and ``-M``, respectively."
    )
    Paragraph(
        "The ``micc2 version`` command also has a ``--tag`` flag that creates a git_ tag "
        "with name ``v<version_string>`` (see https://git-scm.com/book/en/v2/Git-Basics-Tagging) "
        "and pushes the tag to the remote repository."
    )
    process(doc)


if __name__=='__main__':
    TutorialVersionManagement()
    print('-*# finished #*-')
