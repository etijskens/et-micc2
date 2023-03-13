# -*- coding: utf-8 -*-
"""
Module et_micc2.expand
======================

Helper functions for dealing with *Cookiecutter* templates.
"""

import os, shutil, platform
from pathlib import Path
import json

import click

import et_micc2.tools.messages as messages

EXIT_OVERWRITE = -3
__FILE__ = Path(__file__).resolve()

import et_micc2
import et_micc2.tools.tmpl as tmpl


_path_to_templates = Path(et_micc2.__file__).parent / 'templates'


def expand_templates(options):
    for template in options.templates:
        path_to_template = _path_to_templates / template
        if not path_to_template.exists():
            raise RuntimeError(f'Template not found: {path_to_template}')

        if template.startswith('submodule-'):
            if template.endswith('-test'):
                destination = options.project_path / 'tests' / options.package_name / options.module_location_relative
            else:
                destination = options.project_path / options.package_name / options.module_location_relative
        else: # not a sub-module, either top-level package or cli
            destination = options.project_path.parent
        try:
            tmpl.expand_folder(path_to_template, destination, options.template_parameters.data)
        except ValueError as exc:
            return exc.args[0]


def resolve_template(template):
    """Compose the absolute path of a template."""
    
    if  template.startswith('~') or template.startswith(os.sep):
        pass # absolute path
    elif os.sep in template:
        # reative path
        template = Path.cwd() / template
    else:
        # just the template name
        template = Path(__FILE__).parent / 'templates' / template
      
    if not template.exists():
        print(f'template=={template}')
        raise AssertionError(f"Inexisting template {template}")
    
    return template


def set_preferences(micc_file):
    """Set the preferences in *micc_file*.
    
    (This function requires user interaction!)
    
    :param Path micc_file: path to a json file.
    """
    with micc_file.open() as f:
        preferences = json.load(f)

    ty = None
    for parameter,description in preferences.items():
        if not description['default'].startswith('{{ '):
            if 'type' in description:
                ty = description['type']
                description['type'] = eval(ty)
            answer = click.prompt(**description)
            if ty:
                # set the string back
                description['type'] = ty
            preferences[parameter]['default'] = answer
            
    with micc_file.open(mode='w') as f:
        json.dump(preferences, f, indent=2)
        
    return preferences


def get_preferences(micc_file):
    """Get the preferences from *micc_file*.
    
    (This function requires user interaction if no *micc_file* was provided!)

    :param Path micc_file: path to a json file.
    """
    if micc_file.samefile('.'):
        # There is no et_micc2 file with preferences yet.
        dotmicc = Path().home() / '.et_micc2'
        dotmicc.mkdir(exist_ok=True)
        dotmicc_miccfile = dotmicc / 'micc2.json'
        if dotmicc_miccfile.exists():
            preferences = get_preferences(dotmicc_miccfile)
        else:
            preferences = None
            # micc_file_template = Path(__file__).parent / 'micc2.json'
            # shutil.copyfile(str(micc_file_template),str(dotmicc_miccfile))
            # preferences = set_preferences(dotmicc_miccfile)
    else:
        with micc_file.open() as f:
            preferences = json.load(f)

    return preferences


def get_template_parameters(preferences):
    """Get the template parameters from the preferences.
    
    :param dict|Path preferenes:
    :returns: dict of (parameter name,parameter value) pairs.
    """
    if isinstance(preferences,dict):
        template_parameters = {}
        for parameter,description in preferences.items():
            template_parameters[parameter] = description['default']
    elif isinstance(preferences,Path):
        with preferences.open() as f:
            template_parameters = json.load(f)
    else:
        raise RuntimeError()
    
    return template_parameters
