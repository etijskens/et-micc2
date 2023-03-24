# -*- coding: utf-8 -*-

"""
Module et_micc2.project
=======================

An OO interface to *micc* projects.

"""
import copy
from importlib import import_module
import json
from operator import xor
import os
from pathlib import Path
import re
import requests
import shutil
import site
import subprocess
import sys
import sysconfig
from types import SimpleNamespace

import click
import semantic_version

# import et_micc2.tools.config as config
# import et_micc2.tools.expand as expand
import et_micc2.tools.messages as messages
from   et_micc2.tools.tomlfile import TomlFile
import et_micc2.tools.utils as utils


__FILE__ = Path(__file__).resolve()


def is_project_directory(path: Path, project=None) -> bool:
    """Verify that the directory :file:`path` is a project directory. 

    Params:
        path: path to a directory.
        project: if not None, these variables are set:

        * project.project_name
        * project.package_name
        * project.pyproject_toml

    Returns:
         whether the path is a project directory or not.

    As a sufficient condition, we request the presence of

    * a pyproject.toml file, exposing the project's name `[x'tool']['poetry']['name']`
    * a python package with the name `pep8_module_name(name)`.
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


def get_project_path(p: Path) -> Path:
    """Look for a project directory in the parents of path :py:obj:`p`.

    Params:
        p: path to some directory or file.

    Returns:
        the closest containing project directory of `p`

    Raises:
         RuntimeError if p` is not inside a project directory.
    """
    root = Path('/')
    p = Path(p).resolve()
    pp = copy.copy(p)
    while not is_project_directory(pp):
        pp = pp.parent
        if pp == root:
            raise RuntimeError(f"Folder {p} is not in a Python project.")
    return pp


def get_package_path(p: Path) -> Path:
    """Get the package path (top level) from the path `p` to a file or directory in a project.

    Raises:
         RuntimeError if `p` is not in a project.
    """
    project_path = get_project_path(p)
    return project_path / utils.pep8_module_name(project_path.name)


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
            if not getattr(self.context, 'invoked_subcommand', '') in ('create',):
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
        with utils.in_directory(self.context.project_path):
            with open('db.json','w') as f:
                json.dump(self.db, f, indent=2)


    def replace_in_folder( self, folder_path, cur_name, new_name ):
        """replace every occurence of cur_name with new_name in folder folder_path
        """
        cur_dirname = folder_path.name
        new_dirname = cur_dirname.replace(cur_name,new_name)

        with messages.log(self.logger.info, f'Renaming folder: "{cur_dirname}" -> "{new_dirname}"'):
            # first rename the folder
            new_folder_path = folder_path.parent / new_dirname
            os.rename(folder_path, new_folder_path)

            # rename subfolder names:
            folder_list = [] # list of tuples with (oldname,newname)
            for root, folders, files in os.walk(str(new_folder_path)):
                _filter(folders) # in place modification of the list of folders to traverse
                for folder in folders:
                    new_folder = folder.replace(cur_name,new_name)
                    folder_list.append((os.path.join(root,folder), os.path.join(root,new_folder)))

            # rename subfolder names:
            project_path = self.context.project_path
            for old_folder, new_folder in folder_list: # every tuplein the list is automatically unpacked
                self.logger.info(
                    f"Renaming folder '{Path(old_folder).relative_to(self.context.project_path)}'"
                    f"  -> '{Path(new_folder).relative_to(self.context.project_path)}'"
                )
                os.rename(old_folder, new_folder)

            # rename in files and file contents:
            for root, folders, files in os.walk(str(new_folder_path)):
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

        project_path = self.context.project_path
        file = filepath.name
        what = 'Modifying' if contents_only else 'Renaming'
        with messages.log(self.logger.info, f"{what} file '{filepath.relative_to(project_path)}':"):
            self.logger.info(f"Reading file '{filepath.relative_to(project_path)}'")
            with open(filepath,'r') as f:
                old_contents = f.read()

            self.logger.info(f"Replacing '{cur_name}' with '{new_name}' in file contents.")
            new_contents = old_contents.replace(cur_name, new_name)

            if contents_only:
                new_file = file
                new_path = filepath.relative_to(project_path)
            else:
                new_file = file.replace(cur_name,new_name)
                new_path = (filepath.parent / new_file).relative_to(project_path)
                if new_file != file:
                    self.logger.info(f"Replacing '{cur_name}' with '{new_name}' in file name -> '{new_path}'.")

            # By first renaming the original file, we avoid problems when the new file name
            # is identical to the old file name (because it is invariant, e.g. __init__.py)
            orig_file = '.orig.'+file
            orig_path = filepath.parent / orig_file
            self.logger.info(
                f"Keeping original file '{filepath.relative_to(project_path)}'"
                f" as '{orig_path.relative_to(project_path)}'."
            )
            os.rename(filepath, orig_path)

            self.logger.info(f"Writing modified file contents to '{new_path}'.")
            with open(project_path / new_path,'w') as f:
                f.write(new_contents)


def _filter(folders):
    """"In place modification of the list of folders to traverse.

    see https://docs.python.org/3/library/os.html
    """
    exclude_folders = ['.venv', '.git', '_build', '_cmake_build', '__pycache__']
    folders[:] = [f for f in folders if not f in exclude_folders]
