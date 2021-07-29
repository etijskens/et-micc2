# -*- coding: utf-8 -*-
"""Command line interface {{tmpl.app_name}} (no sub-commands)."""

import sys

import click


@click.command()
@click.option('-v', '--verbosity', count=True
             , help="The verbosity of the program."
             , default=1
             )
def main(verbosity):
    """Command line interface {{tmpl.app_name}}.
    
    A 'hello' world CLI example.
    """
    
    for _ in range(verbosity):
        click.echo("running {{tmpl.app_name}}")

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
#eodf
