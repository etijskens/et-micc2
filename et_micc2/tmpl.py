# -*- coding: utf-8 -*-

"""
Package tmpl
=======================================

Top-level package for tmpl.
"""

__version__ = "0.0.0"

import re

def expand(path_to_template, destination, parameters):
    """
    :param Path path_to_template: location of of the template file
    :param Path destination: path to folder where the template file is to be expanded.
        The filename of the destination file is the filename of the template, after replacing
        the parameters
    :param dict parameters: dictionary with the variatbles and their corresponding values.
        All occurences of '{{tmpl.variable}}' in the template file and its filename are
        replaced with parameters[variable].
    """
    # Read the template:
    template = path_to_template.read_text()
    filename = path_to_template.name

    # Expand the template parameters in the template:
    # print(template)
    for parameter,value in parameters.items():
        # print(f"{parameter}={value}")
        s = '{{tmpl.' + parameter +'}}'
        template = template.replace(s, value)
        filename = filename.replace(s, value)
    # print(template)

    # Verify that all parameters in the template are replaced:
    pattern = r'{{tmpl\.(\w+)}}'
    m = re.search(pattern, template)
    if m:
        raise ValueError(f"Missing parameter: '{m[1]}'.")
    m = re.search(pattern, filename)
    if m:
        raise ValueError(f"Missing parameter: '{m[1]}'.")

    # Write the result
    (destination / filename).write_text(template)

