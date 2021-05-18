.. include:: ../HYPERLINKS.rst

.. _git:

5. Version control with Git_
============================

Version control systems (VCS) keep track of modifications to the code in a special
kind of database, called a repository.
`This article <https://www.git-tower.com/learn/git/ebook/en/command-line/basics/why-use-version-control/>`_
explains why version control is important. It is especially important when several
developers work on the same team, but even for one-person development teams, it
brings many advantages. It serves as a backup of the code at different points in time.
If something goes wrong you can go back in time, and compare the version that was
working with the current version and investigate the cause of trouble. For small
projects, the backup is probably the most useful. The local repository of your
project, located on your own hard disk, is often accompanied by a remote repository,
located somewhere in the cloud, e.g. at GitHub_. Then there is a double backup. If your
hard disk crashes, you can recover everything up to the last commit. A remote
repository can also serve as a way to share your code with other people. For larger
projects branching allows you to work on a new feature A of your code without
disturbing the last release (the ``main`` branch). If, at some point, another
feature B seems more urgent, you leave the A branch aside, and start off a new branch for
the B feature from the ``main`` branch. Later, you can resume the work on the A branch.
Finished branches can be merged with the the ``main`` branch, or even a feature
branch. Other typical branches are bug fix branches. Using branches to isolate work
from the main branch, becomes very useful as soon as your code has users. The branches
isolate the users from the ongoing modifications in your bug fix branches and feature
branches.

.. _git-support:

5.1. Git support
----------------

Micc2_ prepares your projects for the Git_ version control system. If you are New to
Git_, we recommend reading
`Introduction to Git In 16 Minutes <https://vickyikechukwu.hashnode.dev/introduction-to-git-in-16-minutes?utm_source=tldrnewsletter>`_.
This article provides a concise introduction to get you going, and some pointers to
more detailed documentation. 

When Micc2_ creates a new project, it automatically sets up a local Git_ repository
and commits the the created project tree with the message 'And so this begun...'.
Micc2_ can also create a remote repository at GitHub_ as well. By default this remote
repository is public, following the spirit of open source development. You can ask
for a private repository by specifying ``--remote-private``, or for no remote
repository at all by specifying ``--remote=none``. If a remote repository is
created, the commit 'And so this begun...' is pushed to the remote repository. For
working with remote Git_ repositories see
`Working with remotes <https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes>`_,
especially checkout the sections 'Pushing to Your Remotes' and 'Fetching and
Pulling from Your Remotes'.

.. note::

   For creating remote repositories for your projects, Micc2_ must be set up correctly.
   See :ref:`micc2 - setup` for details.

Some files and directories are better not stored 

.. _git-workflow:

5.2. Git workflow
-----------------

Some advice for beginners on how to use git_ with your micc project may be appropriate. 

* Use the command ``git status`` to see which project files are modified, and which
  files are new, i.e. are not yet tracked by git_. For new files or directories, you must
  decide whether you want the file or directory to be tracked by git_, or not. If the
  answer is 'yes', tell git_ to track the file or directory with the command ``git add
  <file-or-directory>``. Otherwise, add the file the :file:`.gitignore` file in the
  project directory: ``echo <file-or-directory> >> .gitignore`` (you can also do
  this withe an editor).

* Whenever a piece of work is finished and shows no obvious errors, like syntax errors,
  and passes all the tests, commit the finished work with ``git commit -m <message>``,
  where ``<message>`` describes the piece of work that has been finished. This command
  puts all changes since the last commit in the local repository. New files that haven't
  been added remain untracked. You can commit all untracked files as well by adding the
  ``-a`` flag: ``git commit -a -m <message>``. This first adds all untracked files, as
  in ``git add .`` and than commits. Since, this piece of work is considered finished, it
  is wise to tell the remote repository too about this commit: ``git push``.

* Unfinished pieces of work can be committed too, for backup. In that case, add
  ``WIP`` (work in progress) to the commit message, e.g. ``WIP on feature A``.
  In general, it is best not to push unfinished work to the remote repository, unless it
  is in a separate branch and you are the only one working on it. 

