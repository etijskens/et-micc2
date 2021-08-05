# -*- coding: utf-8 -*-

"""
Package tmpl
=======================================

Top-level package for tmpl.
"""

__version__ = "0.0.0"

import re,os
from pathlib import Path

def expand_string(s, parameters):
    for parameter,value in parameters.items():
        pattern = '{{tmpl.' + parameter +'}}'
        s = s.replace(pattern, value)
    validate(s)
    return s

def validate(s):
    """Verify that there are no more variables to be replaced.

    :param str s: string to be validated
    :raise: ValueError if not fully expanded.
    """
    pattern = r'{{tmpl\.(\w+)}}'
    m = re.search(pattern, s)
    if m:
        raise ValueError(f"Missing parameter: '{m[1]}'.")


def expand_file(root, path_to_template, destination, parameters):
    """Expand a single template file. Both path and contents are expanded.

    :param Path root: path to parent directory of the filepath to be expanded. The root is
        excluded from the expansion.
    :param Path path_to_template: location of of the template file
    :param Path destination: path to folder where the template file is to be expanded, with
        its relative path to root.
    :param dict parameters: dictionary with the variatbles and their corresponding values.
        All occurences of '{{tmpl.variable}}' in the template file and its filename are
        replaced with parameters[variable].
    """
    # Expand the file contents
    template = path_to_template.read_text()
    try:
        template = expand_string(template, parameters)
    except ValueError as exc:
        msg = exc.args[0] + f"\n    while expanding contents of file {path_to_template}."
        raise ValueError(msg)

    # expand the file path
    filepath = str(path_to_template.relative_to(root))
    try:
        filepath = expand_string(filepath, parameters)
    except ValueError as exc:
        msg = exc.args[0] + f"\n    while expanding path of file {path_to_template}."
        raise ValueError(msg)

    # Write the result
    dst = destination / filepath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(template)


def expand_folder(path_to_template_folder, destination, parameters):
    """Expand a template folder.

    :param Path path_to_template_folder: location of the template folder. Only the contents
        of path_to_template_folder are expanded, not the folder itself.
    :param Path destination: path to folder where the template folder is to be expanded.
        The filename of the destination file is the filename of the template, after replacing
        the parameters
    :param dict parameters: dictionary with the variatbles and their corresponding values.
        All occurences of '{{tmpl.variable}}' in the template file and its filename are
        replaced with parameters[variable].
    """
    root = path_to_template_folder
    for d, dirs, files in os.walk(path_to_template_folder):
        for f in files:
            if f != '.DS_Store':
                try:
                    expand_file(root, Path(d) / f, destination, parameters)
                except ValueError as exc:
                    msg = exc.args[0] + f'\n    while expanding template folder {path_to_template_folder}.'
                    raise ValueError(msg)