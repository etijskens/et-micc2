-----------
environment
-----------


* installed windows 10 VM for VirtualBox from
  `Get a Windows 10 development environment <https://developer.microsoft.com/en-us/windows/downloads/virtual-machines>`_
  with guest additions in VirtualBox v6.1.22

* opened cmd prompt (run as administrator), while connected to VPN UAntwerpen:

  .. code-block::

     > slmgr.vbs /skms kms1.ad.ua.ac.be

* installed git version 2.31.1.windows.1

* installed python 3.9.5, from python.org, location: ``C:\Users\User\AppData\Local\Programs\Python\Python39``.
  I needed to **prepend** this to %PATH% in order to get ``python`` to work in the command prompt.

* pip works if run as:

  .. code-block::

     > python -m pip --version
     pip 21.1.1 from C:\Users\User\AppData\Local\Programs\Python\Python39\lib\site-packages\pip (python 3.9)

* Apparently, pip is in ``C:\Users\User\AppData\Local\Programs\Python\Python39\Scripts`` which is not on the 
  path. Micc2 is installed there too. After adding to the PATH, pip works normally, and even micc2 seems ok::

    C:\Users\User>pip --version
    pip 21.1.1 from c:\users\user\appdata\local\programs\python\python39\lib\site-packages\pip (python 3.9)

    C:\Users\User>micc2 --version
    micc2, version 2.4.0

* created workspace and cloned et-micc2 github repo::

    C:\Users\User> mkdir workspace
    C:\Users\User> cd workspace
    C:\Users\User\workspace> git clone https://github.com/etijskens/et-micc2.git
    ...
    C:\Users\User\workspace> cd et-micc2
    C:\Users\User\workspace\eeet-micc2

* install gh::

    C:\Users\User>winget install gh
    Found GitHub CLI [GitHub.cli]
    This application is licensed to you by its owner.
    Microsoft is not responsible for, nor does it grant any licenses to, third-party packages.
    Downloading https://github.com/cli/cli/releases/download/v1.10.2/gh_1.10.2_windows_amd64.msi
      ██████████████████████████████  6.93 MB / 6.93 MB
    Successfully verified installer hash
    Starting package install...
    Successfully installed

* install cmake from cmake.org::

    C:\Users\User>cmake --version
    cmake version 3.20.2
    CMake suite maintained and supported by Kitware (kitware.com/cmake).

* install numpy::

    C:\Users\User>pip install numpy
    Collecting numpy
      Downloading numpy-1.20.3-cp39-cp39-win_amd64.whl (13.7 MB)
        |████████████████████████████████| 13.7 MB 6.8 MB/s
    Installing collected packages: numpy
    Successfully installed numpy-1.20.3

* install pybind11::

    C:\Users\User>pip install pybind11
    Collecting pybind11
      Downloading pybind11-2.6.2-py2.py3-none-any.whl (191 kB)
        |████████████████████████████████| 191 kB 3.3 MB/s
    Installing collected packages: pybind11
    Successfully installed pybind11-2.6.2

* install pytest::

    C:\Users\User>pip install pytest
    Collecting pytest
      Downloading pytest-6.2.4-py3-none-any.whl (280 kB)
        |████████████████████████████████| 280 kB 6.4 MB/s
    Collecting atomicwrites>=1.0
      Downloading atomicwrites-1.4.0-py2.py3-none-any.whl (6.8 kB)
    Collecting colorama
      Downloading colorama-0.4.4-py2.py3-none-any.whl (16 kB)
    Collecting toml
      Downloading toml-0.10.2-py2.py3-none-any.whl (16 kB)
    Collecting iniconfig
      Downloading iniconfig-1.1.1-py2.py3-none-any.whl (5.0 kB)
    Collecting attrs>=19.2.0
      Downloading attrs-21.2.0-py2.py3-none-any.whl (53 kB)
        |████████████████████████████████| 53 kB 1.0 MB/s
    Collecting pluggy<1.0.0a1,>=0.12
      Downloading pluggy-0.13.1-py2.py3-none-any.whl (18 kB)
    Requirement already satisfied: packaging in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from pytest) (20.9)
    Collecting py>=1.8.2
      Downloading py-1.10.0-py2.py3-none-any.whl (97 kB)
        |████████████████████████████████| 97 kB ...
    Requirement already satisfied: pyparsing>=2.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from packaging->pytest) (2.4.7)
    Installing collected packages: toml, py, pluggy, iniconfig, colorama, attrs, atomicwrites, pytest
    Successfully installed atomicwrites-1.4.0 attrs-21.2.0 colorama-0.4.4 iniconfig-1.1.1 pluggy-0.13.1 py-1.10.0 pytest-6.2.4 toml-0.10.2

* install sphinx etc.::

    C:\Users\User>pip install sphinx
    Collecting sphinx
      Downloading Sphinx-4.0.2-py3-none-any.whl (2.9 MB)
        |████████████████████████████████| 2.9 MB 3.3 MB/s
    Collecting sphinxcontrib-htmlhelp
      Downloading sphinxcontrib_htmlhelp-1.0.3-py2.py3-none-any.whl (96 kB)
        |████████████████████████████████| 96 kB 6.8 MB/s
    Collecting snowballstemmer>=1.1
      Downloading snowballstemmer-2.1.0-py2.py3-none-any.whl (93 kB)
        |████████████████████████████████| 93 kB 3.2 MB/s
    Collecting Pygments>=2.0
      Downloading Pygments-2.9.0-py3-none-any.whl (1.0 MB)
        |████████████████████████████████| 1.0 MB 3.3 MB/s
    Requirement already satisfied: docutils<0.18,>=0.14 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (0.17.1)
    Requirement already satisfied: packaging in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (20.9)
    Collecting imagesize
      Downloading imagesize-1.2.0-py2.py3-none-any.whl (4.8 kB)
    Collecting sphinxcontrib-applehelp
      Downloading sphinxcontrib_applehelp-1.0.2-py2.py3-none-any.whl (121 kB)
        |████████████████████████████████| 121 kB 6.8 MB/s
    Collecting sphinxcontrib-jsmath
      Downloading sphinxcontrib_jsmath-1.0.1-py2.py3-none-any.whl (5.1 kB)
    Collecting sphinxcontrib-devhelp
      Downloading sphinxcontrib_devhelp-1.0.2-py2.py3-none-any.whl (84 kB)
        |████████████████████████████████| 84 kB 1.3 MB/s
    Collecting alabaster<0.8,>=0.7
      Downloading alabaster-0.7.12-py2.py3-none-any.whl (14 kB)
    Requirement already satisfied: colorama>=0.3.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (0.4.4)
    Requirement already satisfied: requests>=2.5.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (2.25.1)
    Collecting sphinxcontrib-qthelp
      Downloading sphinxcontrib_qthelp-1.0.3-py2.py3-none-any.whl (90 kB)
        |████████████████████████████████| 90 kB 2.6 MB/s
    Collecting babel>=1.3
      Downloading Babel-2.9.1-py2.py3-none-any.whl (8.8 MB)
        |████████████████████████████████| 8.8 MB 6.4 MB/s
    Collecting sphinxcontrib-serializinghtml
      Downloading sphinxcontrib_serializinghtml-1.1.4-py2.py3-none-any.whl (89 kB)
        |████████████████████████████████| 89 kB 6.1 MB/s
    Requirement already satisfied: setuptools in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (56.0.0)
    Requirement already satisfied: Jinja2>=2.3 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx) (3.0.1)
    Collecting pytz>=2015.7
      Downloading pytz-2021.1-py2.py3-none-any.whl (510 kB)
        |████████████████████████████████| 510 kB 6.4 MB/s
    Requirement already satisfied: MarkupSafe>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from Jinja2>=2.3->sphinx) (2.0.1)
    Requirement already satisfied: idna<3,>=2.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx) (2.10)
    Requirement already satisfied: chardet<5,>=3.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx) (4.0.0)
    Requirement already satisfied: certifi>=2017.4.17 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx) (2020.12.5)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx) (1.26.4)
    Requirement already satisfied: pyparsing>=2.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from packaging->sphinx) (2.4.7)
    Installing collected packages: pytz, sphinxcontrib-serializinghtml, sphinxcontrib-qthelp, sphinxcontrib-jsmath, sphinxcontrib-htmlhelp, sphinxcontrib-devhelp, sphinxcontrib-applehelp, snowballstemmer, Pygments, imagesize, babel, alabaster, sphinx
    Successfully installed Pygments-2.9.0 alabaster-0.7.12 babel-2.9.1 imagesize-1.2.0 pytz-2021.1 snowballstemmer-2.1.0 sphinx-4.0.2 sphinxcontrib-applehelp-1.0.2 sphinxcontrib-devhelp-1.0.2 sphinxcontrib-htmlhelp-1.0.3 sphinxcontrib-jsmath-1.0.1 sphinxcontrib-qthelp-1.0.3 sphinxcontrib-serializinghtml-1.1.4

    C:\Users\User>pip install sphinx-rtd-theme
    Collecting sphinx-rtd-theme
      Downloading sphinx_rtd_theme-0.5.2-py2.py3-none-any.whl (9.1 MB)
        |████████████████████████████████| 9.1 MB 116 kB/s
    Collecting docutils<0.17
      Downloading docutils-0.16-py2.py3-none-any.whl (548 kB)
        |████████████████████████████████| 548 kB 6.8 MB/s
    Requirement already satisfied: sphinx in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx-rtd-theme) (4.0.2)
    Requirement already satisfied: setuptools in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (56.0.0)
    Requirement already satisfied: sphinxcontrib-serializinghtml in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.1.4)
    Requirement already satisfied: sphinxcontrib-devhelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.0.2)
    Requirement already satisfied: sphinxcontrib-applehelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.0.2)
    Requirement already satisfied: sphinxcontrib-jsmath in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.0.1)
    Requirement already satisfied: requests>=2.5.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (2.25.1)
    Requirement already satisfied: colorama>=0.3.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (0.4.4)
    Requirement already satisfied: sphinxcontrib-htmlhelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.0.3)
    Requirement already satisfied: Jinja2>=2.3 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (3.0.1)
    Requirement already satisfied: sphinxcontrib-qthelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.0.3)
    Requirement already satisfied: alabaster<0.8,>=0.7 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (0.7.12)
    Requirement already satisfied: packaging in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (20.9)
    Requirement already satisfied: imagesize in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (1.2.0)
    Requirement already satisfied: snowballstemmer>=1.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (2.1.0)
    Requirement already satisfied: babel>=1.3 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (2.9.1)
    Requirement already satisfied: Pygments>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx->sphinx-rtd-theme) (2.9.0)
    Requirement already satisfied: pytz>=2015.7 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from babel>=1.3->sphinx->sphinx-rtd-theme) (2021.1)
    Requirement already satisfied: MarkupSafe>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from Jinja2>=2.3->sphinx->sphinx-rtd-theme) (2.0.1)
    Requirement already satisfied: chardet<5,>=3.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx->sphinx-rtd-theme) (4.0.0)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx->sphinx-rtd-theme) (1.26.4)
    Requirement already satisfied: idna<3,>=2.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx->sphinx-rtd-theme) (2.10)
    Requirement already satisfied: certifi>=2017.4.17 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx->sphinx-rtd-theme) (2020.12.5)
    Requirement already satisfied: pyparsing>=2.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from packaging->sphinx->sphinx-rtd-theme) (2.4.7)
    Installing collected packages: docutils, sphinx-rtd-theme
      Attempting uninstall: docutils
        Found existing installation: docutils 0.17.1
        Uninstalling docutils-0.17.1:
          Successfully uninstalled docutils-0.17.1
    Successfully installed docutils-0.16 sphinx-rtd-theme-0.5.2

    C:\Users\User>pip install sphinx-click
    Collecting sphinx-click
      Downloading sphinx_click-3.0.0-py3-none-any.whl (8.4 kB)
    Requirement already satisfied: sphinx>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx-click) (4.0.2)
    Requirement already satisfied: docutils in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx-click) (0.16)
    Requirement already satisfied: click>=6.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx-click) (7.1.2)
    Requirement already satisfied: imagesize in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.2.0)
    Requirement already satisfied: sphinxcontrib-serializinghtml in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.1.4)
    Requirement already satisfied: sphinxcontrib-qthelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.0.3)
    Requirement already satisfied: colorama>=0.3.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (0.4.4)
    Requirement already satisfied: alabaster<0.8,>=0.7 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (0.7.12)
    Requirement already satisfied: sphinxcontrib-devhelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.0.2)
    Requirement already satisfied: Jinja2>=2.3 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (3.0.1)
    Requirement already satisfied: babel>=1.3 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (2.9.1)
    Requirement already satisfied: snowballstemmer>=1.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (2.1.0)
    Requirement already satisfied: requests>=2.5.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (2.25.1)
    Requirement already satisfied: setuptools in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (56.0.0)
    Requirement already satisfied: sphinxcontrib-htmlhelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.0.3)
    Requirement already satisfied: packaging in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (20.9)
    Requirement already satisfied: sphinxcontrib-jsmath in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.0.1)
    Requirement already satisfied: sphinxcontrib-applehelp in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (1.0.2)
    Requirement already satisfied: Pygments>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from sphinx>=2.0->sphinx-click) (2.9.0)
    Requirement already satisfied: pytz>=2015.7 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from babel>=1.3->sphinx>=2.0->sphinx-click) (2021.1)
    Requirement already satisfied: MarkupSafe>=2.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from Jinja2>=2.3->sphinx>=2.0->sphinx-click) (2.0.1)
    Requirement already satisfied: chardet<5,>=3.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx>=2.0->sphinx-click) (4.0.0)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx>=2.0->sphinx-click) (1.26.4)
    Requirement already satisfied: certifi>=2017.4.17 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx>=2.0->sphinx-click) (2020.12.5)
    Requirement already satisfied: idna<3,>=2.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests>=2.5.0->sphinx>=2.0->sphinx-click) (2.10)
    Requirement already satisfied: pyparsing>=2.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from packaging->sphinx>=2.0->sphinx-click) (2.4.7)
    Installing collected packages: sphinx-click
    Successfully installed sphinx-click-3.0.0

* install poetry::

    C:\Users\User>pip install poetry
    Collecting poetry
      Downloading poetry-1.1.6-py2.py3-none-any.whl (172 kB)
        |████████████████████████████████| 172 kB 6.8 MB/s
    Collecting shellingham<2.0,>=1.1
      Downloading shellingham-1.4.0-py2.py3-none-any.whl (9.4 kB)
    Requirement already satisfied: packaging<21.0,>=20.4 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from poetry) (20.9)
    Requirement already satisfied: requests<3.0,>=2.18 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from poetry) (2.25.1)
    Collecting html5lib<2.0,>=1.0
      Downloading html5lib-1.1-py2.py3-none-any.whl (112 kB)
        |████████████████████████████████| 112 kB 6.8 MB/s
    Collecting pexpect<5.0.0,>=4.7.0
      Downloading pexpect-4.8.0-py2.py3-none-any.whl (59 kB)
        |████████████████████████████████| 59 kB 4.1 MB/s
    Collecting cleo<0.9.0,>=0.8.1
      Downloading cleo-0.8.1-py2.py3-none-any.whl (21 kB)
    Collecting requests-toolbelt<0.10.0,>=0.9.1
      Downloading requests_toolbelt-0.9.1-py2.py3-none-any.whl (54 kB)
        |████████████████████████████████| 54 kB 1.2 MB/s
    Collecting cachy<0.4.0,>=0.3.0
      Downloading cachy-0.3.0-py2.py3-none-any.whl (20 kB)
    Collecting pkginfo<2.0,>=1.4
      Downloading pkginfo-1.7.0-py2.py3-none-any.whl (25 kB)
    Collecting poetry-core<1.1.0,>=1.0.3
      Downloading poetry_core-1.0.3-py2.py3-none-any.whl (424 kB)
        |████████████████████████████████| 424 kB 6.8 MB/s
    Collecting cachecontrol[filecache]<0.13.0,>=0.12.4
      Downloading CacheControl-0.12.6-py2.py3-none-any.whl (19 kB)
    Collecting virtualenv<21.0.0,>=20.0.26
      Downloading virtualenv-20.4.6-py2.py3-none-any.whl (7.2 MB)
        |████████████████████████████████| 7.2 MB 6.8 MB/s
    Collecting crashtest<0.4.0,>=0.3.0
      Downloading crashtest-0.3.1-py3-none-any.whl (7.0 kB)
    Collecting keyring<22.0.0,>=21.2.0
      Downloading keyring-21.8.0-py3-none-any.whl (32 kB)
    Requirement already satisfied: tomlkit<1.0.0,>=0.7.0 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from poetry) (0.7.1)
    Collecting clikit<0.7.0,>=0.6.2
      Downloading clikit-0.6.2-py2.py3-none-any.whl (91 kB)
        |████████████████████████████████| 91 kB 5.6 MB/s
    Collecting msgpack>=0.5.2
      Downloading msgpack-1.0.2-cp39-cp39-win_amd64.whl (68 kB)
        |████████████████████████████████| 68 kB 4.8 MB/s
    Collecting lockfile>=0.9
      Downloading lockfile-0.12.2-py2.py3-none-any.whl (13 kB)
    Collecting pylev<2.0,>=1.3
      Downloading pylev-1.3.0-py2.py3-none-any.whl (4.9 kB)
    Collecting pastel<0.3.0,>=0.2.0
      Downloading pastel-0.2.1-py2.py3-none-any.whl (6.0 kB)
    Requirement already satisfied: six>=1.9 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from html5lib<2.0,>=1.0->poetry) (1.16.0)
    Collecting webencodings
      Downloading webencodings-0.5.1-py2.py3-none-any.whl (11 kB)
    Collecting pywin32-ctypes!=0.1.0,!=0.1.1
      Downloading pywin32_ctypes-0.2.0-py2.py3-none-any.whl (28 kB)
    Requirement already satisfied: pyparsing>=2.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from packaging<21.0,>=20.4->poetry) (2.4.7)
    Collecting ptyprocess>=0.5
      Downloading ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
    Requirement already satisfied: chardet<5,>=3.0.2 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests<3.0,>=2.18->poetry) (4.0.0)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests<3.0,>=2.18->poetry) (1.26.4)
    Requirement already satisfied: idna<3,>=2.5 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests<3.0,>=2.18->poetry) (2.10)
    Requirement already satisfied: certifi>=2017.4.17 in c:\users\user\appdata\local\programs\python\python39\lib\site-packages (from requests<3.0,>=2.18->poetry) (2020.12.5)
    Collecting distlib<1,>=0.3.1
      Downloading distlib-0.3.1-py2.py3-none-any.whl (335 kB)
        |████████████████████████████████| 335 kB 3.3 MB/s
    Collecting appdirs<2,>=1.4.3
      Downloading appdirs-1.4.4-py2.py3-none-any.whl (9.6 kB)
    Collecting filelock<4,>=3.0.0
      Downloading filelock-3.0.12-py3-none-any.whl (7.6 kB)
    Installing collected packages: pylev, pastel, msgpack, crashtest, webencodings, pywin32-ctypes, ptyprocess, lockfile, filelock, distlib, clikit, cachecontrol, appdirs, virtualenv, shellingham, requests-toolbelt, poetry-core, pkginfo, pexpect, keyring, html5lib, cleo, cachy, poetry
    Successfully installed appdirs-

-------------
testing micc2
-------------

* ``micc2 setup`` goes ok, but the soft link to the 