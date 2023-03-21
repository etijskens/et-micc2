#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for et_micc2 package.
"""
#===============================================================================

import os,re
import shutil
import contextlib
import uuid
import traceback
from pathlib import Path
import subprocess
import time

from click.testing import CliRunner


import et_micc2
from   et_micc2 import cli_micc
import et_micc2.tools.messages as messages
from   et_micc2.tools.tomlfile import TomlFile

def test_workspace(clear = True):
    """return the path to the test workspace, if clear==True, the folder is emptied.

    Params:
        clear: if equal to True the contents of the test workspace are removed. If clear is a str
            it is assumed to refer to the folder to be cleared.
    """
    test_ws = (Path(et_micc2.__file__).parent.parent / '.test-workspace').resolve()

    if clear:
        if 'VSC_HOME' in os.environ:
            # see https://stackoverflow.com/questions/58943374/shutil-rmtree-error-when-trying-to-remove-nfs-mounted-directory
            messages.logging.shutdown()

        if isinstance(clear, str):
            p = test_ws / clear
            if p.is_dir():
                shutil.rmtree(p)
        else:
            if test_ws.exists():
                shutil.rmtree(test_ws)

        test_ws.mkdir(exist_ok=True)

    return test_ws


@contextlib.contextmanager
def in_empty_tmp_dir(cleanup=True):
    """A context manager that creates a temporary folder and changes
    the current working directory to it for isolated filesystem tests.
    
    :param bool cleanup: if True the temporary folder is removed on exit, 
        otherwise a message is printed.
    """
    cwd = Path.cwd()
    uu = uuid.uuid4()
    tmp = cwd / f'__{uu}'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    os.chdir(tmp)
    print("Switching cwd to", tmp)
    try:
        yield tmp
    finally:
        print("Switching cwd back to", cwd)
        os.chdir(cwd)
        if cleanup:
            try:
                shutil.rmtree(tmp)
            except (OSError, IOError):
                pass
        else:
            print(f"Leftover: {tmp}")
        

def get_version(path_to_file,verbose=False):
    version = '?'
    p = str(path_to_file)
    if p.endswith('.toml'):
        tomlfile = TomlFile(path_to_file)
        content = tomlfile.read()
        version = content['tool']['poetry']['version']
    else:
        if p.endswith('.py'):
            with open(str(p)) as f:
                lines = f.readlines() 
                ptrn = re.compile(r"__version__\s*=\s*['\"](.*)['\"]\s*")
                for line in lines:
                    mtch = ptrn.match(line)
                    if mtch:
                        version = mtch[1]
    if verbose:
        print(f"%% {path_to_file} : version : ({version})")
    return version


def micc(arguments, stdin=None, assert_exit_code=True):
    """
    helper function to run cli_micc.py with arguments
    """
    runner = CliRunner()
    result = runner.invoke(cli_micc.main, arguments, input=stdin)

    print(result.output)

    if result.exception:
        if result.stderr_bytes:
            print(result.stderr)
        print('exit_code =', result.exit_code)
        print(result.exception)
        traceback.print_tb(result.exc_info[2])
        print(result.exc_info[2])

    if assert_exit_code:
        if result.exit_code:
            raise AssertionError(f"result.exit_code == {result.exit_code}")

    return result


# ==============================================================================
if __name__ == "__main__":
    pass

# eof #
