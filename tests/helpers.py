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

import et_micc2
test_workspace = (Path(et_micc2.__file__).parent.parent / '.test-workspace').resolve()
print(f"{test_workspace=}")

from et_micc2.tools.tomlfile import TomlFile
import et_micc2.tools.messages as messages



def clear_test_workspace(folder=None):
    """If folder is None, clear the test workspace by removing it and recreating it.
    Otherwise, only remove directory folder
    """
    if 'VSC_HOME' in os.environ:
        # see https://stackoverflow.com/questions/58943374/shutil-rmtree-error-when-trying-to-remove-nfs-mounted-directory
        messages.logging.shutdown()

    if not folder is None:
        p = test_workspace / folder
        if p.exists():
            shutil.rmtree(p)
    else:
        if test_workspace.exists():
            shutil.rmtree(test_workspace)

    test_workspace.mkdir(exist_ok=True)
        

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

    
# ==============================================================================
# ==============================================================================
if __name__ == "__main__":
    pass

# eof #
