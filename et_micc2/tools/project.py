# -*- coding: utf-8 -*-

"""
Module et_micc2.project
=======================

An OO interface to *micc* projects.

"""
import copy
# from importlib import import_module
# import json
# from operator import xor
import os
from pathlib import Path
# import re
# import requests
import shutil
# import site
# import subprocess
# import sys
# import sysconfig
# from types import SimpleNamespace
from typing import List, Tuple

# import click
# import semantic_version

# import et_micc2.tools.config as config
# import et_micc2.tools.expand as expand
import et_micc2.tools.messages as messages
from   et_micc2.tools.tomlfile import TomlFile
import et_micc2.tools.utils as utils
from et_micc2.tools.components import ComponentDatabase


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

        self.components = ComponentDatabase(self.context.project_path)


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


    def replace_in_folder( self,
        folder_path: Path,
        replace: List[Tuple[str, int]],
    ):
        """replace every occurence of replace_what[i] with replace_with[i] in folder folder_path (also
        in file and folder names.

        Params:
            folder_path: path to component to be renamed or removed
            replace: list of tuples (str_to_replace, replacement_str)
        """
        folder_name = folder_path.name
        folder_nam2 = replace_many(folder_name, replace)

        msg = f"replace_in_folder: '{folder_path.relative_to(self.context.project_path)}:'"
        for str_to_replace,replacement in replace:
            msg += f"\n    '{str_to_replace}' -> '{replacement}'"
        with messages.log(self.logger.info, msg):
            # first rename the folder
            if folder_nam2 != folder_name:
                to = folder_path.parent / folder_nam2
                self.logger.info(
                    f"Renaming folder '{folder_path.relative_to(self.context.project_path)}'"
                    f"  -> '{to.relative_to(self.context.project_path)}'"
                )
                folder_path.rename(to)
            else:
                to = folder_path

            # rename subfolder names:
            folder_list = [] # list of tuples with (oldname,newname)
            for root, folders, files in os.walk(str(to)):
                _filter(folders) # in place modification of the list of folders to traverse
                root_path = Path(root)
                for folder in folders:
                    new_folder = replace_many(folder, replace)
                    if new_folder != folder:
                        folder_list.append((root_path / folder, root_path / new_folder))

            # rename subfolder names:
            project_path = self.context.project_path
            for old_folder, new_folder in folder_list: # every tuple in the list is automatically unpacked
                self.logger.info(
                    f"Renaming folder '{old_folder.relative_to(self.context.project_path)}'"
                    f"  -> '{to.relative_to(self.context.project_path)}'"
                )
                old_folder.rename(new_folder)

            # rename in file names and file contents:
            for root, folders, files in os.walk(str(to)):
                root_path = Path(root)
                for file in files:
                    if ( file.startswith('.orig.')
                        or file.endswith('.so')
                        or file.endswith('.json')
                        or file.endswith('.lock')
                    ):
                        continue
                    self.replace_in_file(root_path / file, replace)
                _filter(folders) # in place modification of the list of folders to traverse


    def replace_in_file( self,
        filepath: Path,
        replace: List[Tuple[str,int]],
        contents_only:bool = False
    ):
        """Replace <replace_what> with <replace_with> in file filepath. If `contents_only ==False`
        this action is also performed on the filename.

        Params:
            filepath: path to file
            replace: list of tuples (str_to_replace, replacement_str)
            contents_only: if True the filename is not changed
        """
        project_path = self.context.project_path
        file = filepath.name
        what = 'Modifying' if contents_only else 'Renaming'
        with messages.log(self.logger.info, f"{what} file '{filepath.relative_to(project_path)}':"):
            self.logger.info(f"Reading file comtents from '{filepath.relative_to(project_path)}'")
            with open(filepath,'r') as f:
                old_contents = f.read()
            new_contents = replace_many(old_contents, replace)
            contents_modified = new_contents != old_contents

            if contents_only:
                new_file = file
                new_path = filepath.relative_to(project_path)
                filename_modified = False
            else:
                new_file = replace_many(file,replace)
                filename_modified = new_file != file
                new_path = (filepath.parent / new_file).relative_to(project_path)

            text = ("modified file name and contents" if (contents_modified and filename_modified) else
                   ("modified file contents"          if (contents_modified) else
                   ("modified file name"              if (filename_modified) else
                   ("unchanged file"))))
            self.logger.info(f"Replacing '{replace}': {text} -> '{new_path}'.")

            if filename_modified or contents_modified:
                # By first renaming the original file, we avoid problems when the new file name
                # is identical to the old file name (because it is invariant, e.g. __init__.py)
                orig_file = '.orig.'+file
                orig_path = filepath.parent / orig_file
                self.logger.info(
                    f"Keeping original file '{filepath.relative_to(project_path)}'"
                    f" as '{orig_path.relative_to(project_path)}'."
                )
                filepath.rename(orig_path)
                with open(project_path / new_path,'w') as f:
                    f.write(new_contents)
                self.logger.info(f"Writing file contents to '{new_path}'")


    def remove_file(self, path: Path):
        path.unlink(missing_ok=True)


    def remove_folder(self, path):
        shutil.rmtree(path)

    def serialize(self, new_components=[]):
        self.components.serialize(new_components=new_components, logger=self.context.logger)

def _filter(folders):
    """"In place modification of the list of folders to traverse.

    see https://docs.python.org/3/library/os.html
    """
    exclude_folders = ['.venv', '.git', '_build', '_cmake_build', '__pycache__']
    folders[:] = [f for f in folders if not f in exclude_folders]

def replace_many(s:str, replace: List[Tuple[str,str]]) -> str:
    """Replacing many strings in a str.

    Params:
        s : str to be modified
        replace: list of tuples (str_to_replace, replacement_str)
    """
    result = s
    for str_to_replace,replacement in replace:
        result = result.replace(str_to_replace, replacement)
    return result