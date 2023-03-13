import os
from pathlib import Path

import click

from et_micc2.subcmds.add import get_submodule_type

def info(project):
    """Output info on the project."""

    # This command does not require any external tools.

    if project.context.verbosity >= 0:
        project.context.verbosity = 10

    if project.context.verbosity >= 1:
        click.echo(
            "Project " + click.style(str(project.context.project_path.name), fg='green')
            + " located at " + click.style(str(project.context.project_path), fg='green')
            + "\n  package: " + click.style(str(project.context.package_name), fg='green')
            + "\n  version: " + click.style(project.version, fg='green')
        )

    if project.context.verbosity >= 3:
        click.echo("  contents:")
        lines = []
        top = project.context.project_path / project.context.package_name
        for d, dirs, files in os.walk(top):
            if '_cmake_build' in d:
                continue
            pd = Path(d)
            submodule_type = get_submodule_type(pd)
            pdr = pd.relative_to(project.context.project_path)
            if pd == top:
                tp = 'top-level package      (source in '
                src = str(pdr / '__init__.py')
            else:
                if submodule_type == 'py':
                    tp = f'Python submodule       (source in '
                    src = f'{pdr}/__init__.py'
                elif submodule_type == 'f90':
                    tp = f'Fortran submodule      (source in '
                    src = f'{pdr}/{pdr.name}.f90'
                elif submodule_type == 'cpp':
                    tp = f'C++ submodule          (source in '
                    src = f'{pdr}/{pdr.name}.cpp'
                else:
                    continue
            lines.append((str(pdr), tp, src))
            if pd == top:
                for file in files:
                    if file.startswith('cli_') and file.endswith('.py'):
                        lines.append((f'{pd.name}{os.sep}{file}', 'Command Line Interface', ''))
        w = 0
        for line in lines:
            w = max(w, len(line[0]))
        w += 2
        for line in lines:
            s = '    ' + str(line[0]).ljust(w)
            click.echo(
                click.style(s, bold=True) +
                click.style(line[1]) +
                click.style(line[2], fg='green') +
                (')' if line[2] else '')
            )

