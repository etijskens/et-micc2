# -*- coding: utf-8 -*-

"""
Module et_micc2.project
=======================

An OO interface to *micc* projects.

"""
from copy import copy
import os, sys, site, subprocess, re
import sysconfig
import shutil
import json
from pathlib import Path
from operator import xor
import requests
from types import SimpleNamespace
from importlib import import_module

import click
import semantic_version

import et_micc2.tools.config as config
import et_micc2.tools.utils as utils
import et_micc2.tools.expand as expand
import et_micc2.tools.messages as messages
from et_micc2.tomlfile import TomlFile


__FILE__ = Path(__file__).resolve()
_exit_missing_component = -1


def is_project_directory(path, project=None):
    """Verify that the directory :file:`path` is a project directory. 

    :param Path path: path to a directory.
    :param Project project: if not None these variables are set:

        * project.project_name
        * project.package_name
        * project.pyproject_toml

    :returns: bool.

    As a sufficident condition, we request that 

    * there is a pyproject.toml file, exposing the project's name:py:obj:`['tool']['poetry']['name']`
    * that there is a python package or module with that name, converted by :py:meth:`pep8_module_name`.
    """
    if not isinstance(path, Path):
        path = Path(path)

    path_to_pyproject_toml = str(path / 'pyproject.toml')

    try:
        pyproject_toml = TomlFile(path_to_pyproject_toml)
        if not project is None:
            project.pyproject_toml = pyproject_toml
            # project.project_name = project_name
    except Exception:
        return False

    return verify_project_structure(path, project)


def verify_project_structure(path, project=None):
    """Verify that there is either a Python module :file:`<package_name>.py`, or
    a package :file:`<package_name>/__init__.py` (and not both).

    :returns: a list with what was found. This list should have length 1. If its
        length is 0, neither module.py, nor module/__init__.py were found. If its
        length is 2, both were found.
    """
    package_name = utils.pep8_module_name(path.name)

    module = path / (package_name + ".py")
    module = str(module.relative_to(path)) if module.is_file() else ""

    package = path / package_name / "__init__.py"
    package = str(package.relative_to(path)) if package.is_file() else ""

    if package and module:
        if project:
            messages.error(f"Package ({package_name}/__init__.py) and module ({package_name}.py) found.")
        return False
    elif (not module and not package):
        if project:
            messages.error(f"Neither package ({package_name}/__init__.py) nor module ({package_name}.py) found.")
        return False
    else:
        if project:
            project.context.package_name = package_name
        return True


class Project:
    """
    An OO interface to *micc* projects.

    :param types.SimpleNameSpace context: all options from the ``micc`` CLI.
    """

    def __init__(self, context):
        self.context = context

        if hasattr(context, 'template_parameters'):
            # only needed for expanding templates.
            # Pick up the default parameters
            parameters = self.context.preferences
            parameters.update(context.template_parameters)
            context.template_parameters = parameters

        self.logger = None
        if is_project_directory(self.context.project_path, self):
            self.get_logger()
        else:
            # Not a project directory, only create and setup subcommands can work,
            # (but setup does not construct a Project object).
            if not self.context.invoked_subcommand in ('create',):
                messages.error(f'Not a project directory: `{self.context.project_path}`')


    @property
    def version(self):
        """Return the project's version (str)."""
        return self.pyproject_toml['tool']['poetry']['version']


    def get_logger(self, log_file_path=None):
        """"""
        if self.logger:
            return

        if log_file_path:
            log_file_name = log_file_path.name
            log_file_dir = log_file_path.parent
        else:
            log_file_name = f"{self.context.project_path.name}.micc.log"
            log_file_dir = self.context.project_path
            log_file_path = log_file_dir / log_file_name
        self.log_file = log_file_path

        if getattr(self.context, 'clear_log', False):
            if log_file_path.exists():
                log_file_path.unlink()

        # create a new logger object that will write to the log file and to the console
        self.logger = messages.create_logger(log_file_path)

        # set the log level from the verbosity
        self.logger.console_handler.setLevel(messages.verbosity_to_loglevel(self.context.verbosity))

        if self.context.verbosity > 2:
            print(f"Current logfile = {log_file_path}")

        if getattr(self.context, 'clear_log', False):
            self.logger.info(f"The log file was cleared: {log_file_path}")
            self.context.clear_log = False

        self.context.logger = self.logger


    def deserialize_db(self):
        """Read file ``db.json`` into self.db."""

        db_json = self.context.project_path / 'db.json'
        if db_json.exists():
            with db_json.open('r') as f:
                self.db = json.load(f)
        else:
            self.db = {}


    def serialize_db(self, db_entry=None, verbose=False):
        """Write self.db to file ``db.json``.

        Self.context is a SimpleNamespace object which is not default json serializable.
        This function takes care of that by converting to ``str`` where possible, and
        ignoring objects that do not need serialization, as e.g. self.context.logger.
        """

        if db_entry:
            # produce a json serializable version of db_entry['context']:
            my_options = {}
            for key, val in db_entry['context'].__dict__.items():
                if isinstance(val,(dict, list, tuple, str, int, float, bool)):
                    # default serializable types
                    my_options[key] = val
                    if verbose:
                        print(f"serialize_db: using ({key}:{val})")
                elif isinstance(val, Path):
                    my_options[key] = str(val)
                    if verbose:
                        print(f"serialize_db: using ({key}:str('{val}'))")
                else:
                    if verbose:
                        print(f"serialize_db: ignoring ({key}:{val})")

            db_entry['context'] = my_options

            if not hasattr(self, 'db'):
                # Read db.json into self.db if self.db does not yet exist.
                self.deserialize_db()

            # store the entry in self.db:
            self.db[self.context.add_name] = db_entry

        # finally, serialize self.db
        with et_micc2.utils.in_directory(self.context.project_path):
            with open('db.json','w') as f:
                json.dump(self.db, f, indent=2)


    def replace_in_folder( self, folderpath, cur_name, new_name ):
        """"""
        cur_dirname = folderpath.name
        new_dirname = cur_dirname.replace(cur_name,new_name)

        with messages.log(self.logger.info, f'Renaming folder "{cur_dirname}" -> "{new_dirname}"'):
            # first rename the folder
            new_folderpath = folderpath.parent / new_dirname
            os.rename(folderpath, new_folderpath)

            # rename subfolder names:
            folder_list = [] # list of tuples with (oldname,newname)
            for root, folders, files in os.walk(str(new_folderpath)):
                _filter(folders) # in place modification of the list of folders to traverse
                for folder in folders:
                    new_folder = folder.replace(cur_name,new_name)
                    folder_list.append((os.path.join(root,folder), os.path.join(root,new_folder)))

            # rename subfolder names:
            for tpl in folder_list:
                old_folder = tpl[0]
                new_folder = tpl[1]
                self.logger.info(f"Renaming folder '{old_folder}'  -> '{new_folder}'")
                os.rename(old_folder, new_folder)

            # rename in files and file contents:
            for root, folders, files in os.walk(str(new_folderpath)):
                for file in files:
                    if file.startswith('.orig.'):
                        continue
                    if file.endswith('.so'):
                        continue
                    if file.endswith('.json'):
                        continue
                    if file.endswith('.lock'):
                        continue
                    self.replace_in_file(Path(root) / file, cur_name, new_name)
                _filter(folders) # in place modification of the list of folders to traverse


    def remove_file(self,path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


    def remove_folder(self,path):
        shutil.rmtree(path)


    def replace_in_file(self, filepath, cur_name, new_name, contents_only=False):
        """Replace <cur_name> with <new_name> in the filename and its contents."""

        file = filepath.name

        what = 'Modifying' if contents_only else 'Renaming'
        with messages.log(self.logger.info, f"{what} file {filepath}:"):
            self.logger.info(f'Reading from {filepath}')
            with open(filepath,'r') as f:
                old_contents = f.read()

            self.logger.info(f'Replacing "{cur_name}" with "{new_name}" in file contents.')
            new_contents = old_contents.replace(cur_name, new_name)

            if contents_only:
                new_file = file
            else:
                new_file = file.replace(cur_name,new_name)
                self.logger.info(f'Replacing "{cur_name}" with "{new_name}" in file name -> "{new_file}"')
            new_path = filepath.parent / new_file

            # By first renaming the original file, we avoid problems when the new
            # file name is identical to the old file name (because it is invariant,
            # e.g. __init__.py)
            orig_file = '.orig.'+file
            orig_path = filepath.parent / orig_file
            self.logger.info(f'Keeping original file "{file}" as "{orig_file}".')
            os.rename(filepath, orig_path)

            self.logger.info(f'Writing modified file contents to {new_path}: ')
            with open(new_path,'w') as f:
                f.write(new_contents)


def _filter(folders):
    """"In place modification of the list of folders to traverse.

    see https://docs.python.org/3/library/os.html

    ...

    When topdown is True, the caller can modify the dirnames list in-place
    (perhaps using del or slice assignment), and walk() will only recurse
    into the subdirectories whose names remain in dirnames; this can be used
    to prune the search, impose a specific order of visiting, or even to
    inform walk() about directories the caller creates or renames before it
    resumes walk() again. Modifying dirnames when topdown is False has no
    effect on the behavior of the walk, because in bottom-up mode the
    directories in dirnames are generated before dirpath itself is generated.

    ...
    """
    exclude_folders = ['.venv', '.git', '_build', '_cmake_build', '__pycache__']
    folders[:] = [f for f in folders if not f in exclude_folders]
