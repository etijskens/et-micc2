# -*- coding: utf-8 -*-

"""
Package {{tmpl.package_name}}
=======================================

Top-level package for {{tmpl.package_name}}.
"""

__version__ = "{{tmpl.version}}"


def hello(who='world'):
    """'Hello world' method.

    :param str who: whom to say hello to
    :returns: a string
    """
    result = "Hello " + who
    return result

# Your code here...