#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for et_micc2.logger module."""

from pathlib import Path
import types

import et_micc2.project
import et_micc2.utils
import et_micc2.logger

def test_log():
    with et_micc2.logger.log():
        print('test_log without logfun')
        
    logfile = et_micc2.utils.get_project_path('.') / 'et_micc2.log'
    print(logfile.resolve())
    if logfile.exists():
        logfile.unlink()
    assert not logfile.exists()

    options = types.SimpleNamespace(verbosity=3
                                          ,project_path=Path().resolve()
                                          ,clear_log=False
                                          )
    project = et_micc2.project.Project(options)

    with et_micc2.logger.logtime(project):
        with et_micc2.logger.log(project.logger.info):
            project.logger.info('test_log with a logfun')
            project.logger.debug('debug message\nwith 2 lines')
    logfile = project.log_file
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
