#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for messages module."""

from pathlib import Path
import types

import et_micc2.tools.project as project
import et_micc2.tools.utils as utils
import et_micc2.tools.messages as messages

def test_log():
    with messages.log():
        print('test_log without logfun')
        
    logfile = utils.get_project_path('.') / 'et_micc2.log'
    print(logfile.resolve())
    if logfile.exists():
        logfile.unlink()
    assert not logfile.exists()

    options = types.SimpleNamespace(
        verbosity=3,
        project_path=Path().resolve(),
        clear_log=False
    )
    proj = project.Project(options)

    with messages.logtime(proj):
        with messages.log(proj.logger.info):
            proj.logger.info('test_log with a logfun')
            proj.logger.debug('debug message\nwith 2 lines')
    logfile = proj.log_file
    assert logfile.exists()
    logtext = logfile.read_text()
    print(logtext)
    assert "doing" in logtext
    assert "test_log with a logfun\n" in logtext
    assert "debug message" in logtext
    assert "done." in logtext
    

# ==============================================================================
# The code below is for debugging a particular test in eclipse/pydev.
# (normally all tests are run with pytest)
# ==============================================================================
if __name__ == "__main__":
    the_test_you_want_to_debug = test_log

    print(f"__main__ running {the_test_you_want_to_debug}")
    the_test_you_want_to_debug()
    print('-*# finished #*-')
# ==============================================================================
