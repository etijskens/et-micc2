# -*- coding: utf-8 -*-
"""
module config
=============

"""
from pathlib import Path
import json
import click

class Config:
    """Class for configuration (or preferences) files.

    In fact little more than a persistent dict."""

    # this key controls the file location of the Config file
    file_key = 'file_loc'

    def __init__(self, **kwargs ):
        """"""
        self.data = {}

        if Config.file_key in kwargs:
            # Read Config object data
            p_cfg = Path(kwargs[Config.file_key])
            self.load(p_cfg)

        # Add the other kwargs
        kwargs.pop(Config.file_key,None)
        self.add(**kwargs)

    def load(self, p_cfg):
        """

        :param Path p_cfg: path to cfg file
        """
        if p_cfg.is_absolute():
            if p_cfg.exists():
                self.p_cfg = p_cfg
            else:
                raise FileNotFoundError(p_cfg)
        else:
            # first look in the current directory
            if p_cfg.exists():
                self.p_cfg = p_cfg.resolve()

            # then look in the home directory:
            elif (Path.home() / p_cfg.name).exists():
                self.p_cfg = Path.home() / p_cfg.name
            
            else:
                raise FileNotFoundError(p_cfg.name)

        with self.p_cfg.open() as fp_cfg:
            data = json.load(fp_cfg)
            self.data.update(data)
        self.update_location_(self.p_cfg)


    def save(self, file='', mkdir=False):
        """Save self.data to cfg file. If file is not specified """
        if file:
            p_cfg =  Path(file)
        elif Config.file_key in self.data:
            p_cfg = Path(self.data[Config.file_key])
        else:
            raise RuntimeError("Don't have a file location to save to.")

        p_cfg = self.p_cfg if not file else Path(file)
        p_cfg = p_cfg.resolve()
        if not p_cfg.parent.exists():
            if mkdir:
                p_cfg.parent.mkdir()
            else:
                print(f'Inexisting Path: {p_cfg.parent}. Create it yourself, or use the "mkdir=True" parameter.')
                raise FileNotFoundError()
        self.update_location_(p_cfg)

        with p_cfg.open('w') as fp_cfg:
            json.dump(self.data, fp_cfg, indent=2)


    def add(self, **kwargs):
        self.data.update(kwargs)


    # "Private" methods: For internal use only.
    def update_location_(self, p_cfg):
        """Make sure self.data[Config.file_key] points to the correct location, i.e. where the Config object was
        Read from or written to.

        For internal use only.
        """
        self.data[Config.file_key] = str(p_cfg)


    def __str__(self):
        return json.dumps(self.data,indent=2)


    def __getitem__(self, item):
        return self.data[item]


    def __setitem__(self, key, value):
        self.data[key] = value

    
    def update(self,dict):
        self.data.update(dict)

def get_answer():
    """Get answer str, raise KeyboardInterrupt if answer contains `^^`."""
    click.secho('Enter `^^` to exit.', fg='white')
    answer = input('>: ')
    if '^^' in answer:
        raise KeyboardInterrupt
    return answer


def get_param(name,description):
    """"""
    if 'default' in description:
        default = description["default"]
        click.echo(f'\nEnter {description["text"]}. Default = [{click.style(default,fg="green")}]')
        answer = get_answer()
        if not answer:
            answer = default

    elif 'choices' in description:
        choices = description["choices"]
        click.echo(f'\nEnter {description["text"]} [{click.style(choices[0],fg="blue")}]\nChoose between:')
        for i,choice in enumerate(choices):
            if i ==0 :
                click.echo(f'  {i}: {click.style(choice, fg="green")} (default)')
            else:
                click.echo(f'  {i}: {click.style(choice, fg="blue")}')

        while 1:
            answer = get_answer()
            if not answer:
                answer = choices[0]
                break
            try:
                i = int(answer)
                answer = choices[i]
                break
            except ValueError:
                result = []
                for choice in choices:
                    if choice.startswith(answer):
                        result.append(choice)
                if len(result) == 1:
                    answer = result[0]
                    break
                    
        print(f'>: {answer}')

    else:
        click.echo(f'\nEnter {description["text"]}')

        while 1:
            answer = get_answer()
            if answer:
                break

    pp = description.get('postprocess', None)
    if pp:
        answer = pp(answer)

    return answer

# eof
