# -*- coding: utf-8 -*-
"""
Module et_micc2.tools.messages
======================

Helper functions for logging.
"""

from contextlib import contextmanager
from datetime import datetime
from enum import Enum
import logging
import sys

import click

ExitCodes = Enum(
    'ExitCodes',
    [ 'MISSING_COMPONENT'
    , 'Overwrite'
    , 'USER_INTERRUPTION'
    , 'SUBMODULE_NOT_FOUND'
    , 'RuntimeError'
    , 'COMPONENT_NAME_NOT_UNIQUE'
    ]
)


def verbosity_to_loglevel(verbosity):
    """Tranlate :py:obj:`verbosity` into a loglevel.

    :param int verbosity:
    """
    if verbosity==0:
        return logging.CRITICAL
    elif verbosity==1:
        return logging.INFO
    else:
        return logging.DEBUG


# # Use static vare to implement a singleton (the micc_logger)
# @static_vars(the_logger=None)
# def get_micc_logger(global_options=None):
#     """Set up and store a et_micc2 logger that writes to the console (taking verbosity
#     into account) and to a log file ``et_micc2.log``.
#
#     :param types.SimpleNamespace global_options: namespace object with options
#         accepted by (almost) all et_micc2 commands. If None, the static :py:obj:`the_logger`
#         is returned.
#     :returns: a Logger object.
#     """
#
#     # if global_options is None:
#     #     if get_micc_logger.the_logger is None:
#     #         raise RuntimeError("Micc logger not created yet - this is a bug.")
#     #     return get_micc_logger.the_logger
#
#     if not get_micc_logger.the_logger is None:
#         # verify that the current logger is for the current project directory
#         # (When running pytest, et_micc2 commands are run in several different
#         # project directories created on the fly. the micc_logger must adjust
#         # to this situation and log to a et_micc2.log file in the project directory.
#         current_logfile = get_micc_logger.the_logger.use_logfile
#         current_project_path = global_options.project_path
#         if not current_logfile.parent == current_project_path:
#             get_micc_logger.the_logger = None
#
#     if get_micc_logger.the_logger is None:
#
#         if getattr(global_options,'clear_log',False):
#             use_logfile = global_options.project_path / 'et_micc2.log'
#             if use_logfile.exists():
#                 use_logfile.unlink()
#             else:
#                 global_options.clear_log = False
#
#         # create a new logger object that will write to et_micc2.log
#         # in the current project directory
#         p = global_options.project_path / 'et_micc2.log'
#         get_micc_logger.the_logger = create_logger(p)
#         get_micc_logger.the_logger.use_logfile = p
#         if global_options.verbosity>2:
#             print(f"micc_logger.use_logfile = {get_micc_logger.the_logger.use_logfile}")
#
#
#     # set the log level from the verbosity
#     get_micc_logger.the_logger.console_handler.setLevel(verbosity_to_loglevel(global_options.verbosity))
#
#     if getattr(global_options,'clear_log',False):
#         global_options.clear_log = False
#         get_micc_logger.the_logger.debug("The log file was cleared.")
#
#     return get_micc_logger.the_logger
#

class IndentingLogger(logging.Logger):
    """Cuastom Logger class for creating indented logs.
    
    This is the class for the et_micc2 logger.
    """
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._indent = ''
        self._stack = []
        
        
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """Overloaded functon from logging.Logger"""
        msg = msg.strip()
        # ensure that the indentation is independent of the lenght of the levelname.
        w = (10-len(logging.getLevelName(level))) * ' '
        if self._indent:
            msg = w + self._indent + msg.replace('\n','\n' + 10*' ' + w + self._indent)
        super()._log(level, msg, args, exc_info, extra)
        
            
    def indent(self,n=4):
        """Increase the indentation level.
        
        Future log messages will shift to the right by n spaces.
        """
        self._indent += n*' '
        self._stack.append(n)
        
            
    def dedent(self):
        """Increase the indentation level.
        
        Future log messages will shift to the left. The width of the shift
        is determined by the last call to :py:meth:`~et_micc2.logger.IndentingLogger.indent`
        """
        if self._stack:
            n = self._stack.pop()
            length = len(self._indent) - n
            self._indent = self._indent[0:length]


def create_logger(path_to_log_file,filemode='a'):
    """Create a logger object for et_micc2.
    
    It will log to:
    
    * the console
    * file *path_to_log_file*. By default log message will be appended to the
    """
    use_logfile = False
    # create formatters and add it to the handlers
    format_string = f"[%(levelname)s] %(message)s"
    console_formatter = logging.Formatter(format_string)
    if use_logfile:
        logfile_formatter = logging.Formatter(format_string)

    # create and add a console handler 
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(1)

    if use_logfile:
        # create and add a use_logfile handler
        logfile_handler = logging.FileHandler(path_to_log_file,mode=filemode)
        logfile_handler.setFormatter(logfile_formatter)
        logfile_handler.setLevel(logging.DEBUG)
            
    # create logger
    logger = IndentingLogger(name="ok")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    if use_logfile:
        logger.addHandler(logfile_handler)

    # add the handlers as a member, so we can still modify them on the fly.
    logger.console_handler = console_handler
    logger.log_file = None
    if use_logfile:
        logger.logfile_handler = logfile_handler
        logger.log_file = path_to_log_file
    return logger


@contextmanager
def log(logfun=None, before='doing', after='done.',bracket=True):
    """Print a message before and after executing the body of the contextmanager.

    :param callable logfun: a function that can print a log message, e.g. :py:meth:`print`, :py:meth:`~et_micc2.logger.get_micc_logger.the_logger.info`.
    :param str before: print this before body is executed
    :param str after: print this after body is executed
    :param bool bracket: append ' [' to before and prepend '] ' to after.
    
    This works best with the :py:class:`~et_micc2.logger.IndentingLogger`.
    """
    if logfun:
        if bracket:
            msg = '[ ' + before
        logfun(msg)
        try:
            logfun.__self__.indent()
            is_logger = True
        except AttributeError:
            is_logger = False
    yield
    if logfun:
        if is_logger:
            logfun.__self__.dedent()
        if bracket:
            msg = '] '+ after
        logfun(msg)


@contextmanager
def logtime(project=None):
    """Log start time, end time and duration of the task in the body of the context manager
    to the et_micc2 logger.
    
    This logs on debug level. To see in in the console output you must pass ``-vv`` to et_micc2.
    
    :param SimpleNameSpace global_options: pass verbosity to the et_micc2 logger.
    """
    if project is None:
        logfun = print
    else:
        logfun = getattr(project.logger, 'debug', print)

    start = datetime.now()
    logfun(f"start = {start}")
    logfun.__self__.indent()

    yield
    logfun.__self__.dedent()
    stop = datetime.now()
    logfun(f"stop  = {stop}")
    spent = stop - start
    logfun(f"spent = {spent}")


def error(msg: str, exit_code=None):
    """Print an error message, and raise a RuntimeError if the exit_code is not None.
    The exit code is stored in the error

    Params:
        msg: the error message
        exit_code: the exit_code to report
    """
    click.secho("[ERROR]\n" + msg, fg='bright_red')
    if exit_code:
        runtime_error = RuntimeError(msg)
        runtime_error.exit_code = exit_code
        raise runtime_error

def warning(msg):
    """Print a warning message ``msg``."""
    click.secho("[WARNING]\n" + msg, fg='green')


def ask_user_to_continue_or_not(default_answer=False, stop_message='Exiting.'):
    """Ask the user if he wants to continue or stop a command.

    Params:
        default_answer: The answer, if the user just presses enter.
        stop_message: message printed if the user answers 'no'.

    Returns: True if the user wants to stop, False otherwise.
    """
    question = 'Continue? [Yes]/No' if default_answer else 'Continue? [No]/Yes'
    answer = input(question)

    if not answer:
        answer = default_answer
    else:
        answer = answer.lower()
        answer = True if answer.startswith('y') or answer == '1' else False

    if not answer:
        error(stop_message, exit_code=ExitCodes.USER_INTERRUPTION)


