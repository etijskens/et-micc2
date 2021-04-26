# Script for installing the project in the current Python environment in editable mode

import sys
import subprocess
from pathlib import Path
import shutil
import os
import pkg_resources

import click

def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    result = getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix
    # print(f"get_base_prefix_compat() = {result}")
    return result


def in_virtualenv():
    return get_base_prefix_compat() != sys.prefix


@click.command()
@click.argument('project', default='.')
def main(project):
    """Make an editable install of project `project` in the Python environment with which
    this script was called. Editable installs make changes to your project's source code
    instantly visible in the environment, so they can be tested and debugged.

    This script is a work around for ``pip install -e path/to/project`` which fails for
    micc projects because pip requires a ``setup.py`` file for editable installs.

    This script may be called with *any* Python executable, not necessarily the one of
    yoyr Micc2 environment. The project's package will bee installed in the site-packages
    of the calling Python. If the calling Python is not in a virtual environment the project
    is installed with the `--user` flag to avoid cluttering the system Python's site-packages.

    :param str project: path to the project to install, defaults to CWD.
    """
    if len(sys.argv) > 1:
        project = sys.argv[1]
    project_path = Path(project).resolve()

    if not project_path.exists():
        raise RuntimeError(f"Project path {project_path} does not exist.")

    if not project_path.is_dir():
        raise RuntimeError(f"Not a project directory: {project_path}.")

    if not (project_path / 'pyproject.toml').is_file():
        raise RuntimeError(f"Not a project directory: {project_path}.")

    project_name = project_path.name
    package_name = project_name.replace('-', '_').lower()

    package_path = (project_path / package_name)
    if package_path.is_dir():
        if not (package_path / '__init__.py').is_file():
            raise RuntimeError(f"Not a project directory: {project_path}. (Package {package_name} not found.)")
        else:
            structure = 'package'
    else:
        if not (project_path / f'{package_name}.py').is_file():
            raise RuntimeError(f"Not a project directory: {project_path}. (Module {package_name} not found.)")
        else:
            structure =' module'

    if in_virtualenv():
        user_flag = False
        environment = click.style('virtual environment',fg='red')
    else:
        user_flag = True
        environment = click.style('current Python environment',fg='red')
        # print(f'Install (editable) project {project_name} in current Python environment {sys.prefix} with `--user`?')

    click.echo(f"Create editable install of project `{click.style(project_name,fg='blue',bold=True)}` in {environment} (={click.style(sys.prefix,bold=True)})?")
    while 1:
        answer = input('Proceed (yes/no)? ')
        if answer.lower().startswith('n'):
            print('Interrupted.')
            sys.exit(-1)
        if answer == '' or answer.lower().startswith('y'):
            break
    print("\nProceeding ...")
    # install, not editable
    cmd = [sys.executable, "-m", "pip", "install", '.']
    if user_flag:
        cmd.insert(4,'--user')
    click.secho(f"> {' '.join(cmd)}",fg='green')
    subprocess.check_call(cmd)
    try:
        pkg_dist_info = pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        click.secho(f'Package {package_name} not found.', fg='red')
        raise
    else:
        location = pkg_dist_info.location
        click.secho(f'Package `{package_name}` installed at `{location}`.\n', fg='green')

    # make installation editable
    if structure == 'package':
        package_path = Path(location) / package_name
        click.secho(f'Removing package: {package_path}', fg='green')
        if package_path.is_symlink():
            package_path.unlink()
        else:
            shutil.rmtree(package_path)
        
        # Occasionally, we must remove a module file. If the project had a module structure, but
        # was recently converted to a package structure, an orphan module file (package_name.py)
        # may be left in the site-packages directory
        module = f'{package_name}.py'
        module_path = package_path / module
        if module_path.exists():
            module_path.unlink()
            
        click.secho(f'Replacing package with symbolic link: {project_path / package_name}', fg='green')
        os.symlink(src=(project_path / package_name), dst=package_path)

    else: # module structure
        module = f'{package_name}.py'
        package_path = Path(location) / module
        click.secho(f'Removing package: {package_path}', fg='green')
        package_path.unlink()
        click.secho(f'Replacing package with symbolic link: {project_path / module}', fg='green')
        os.symlink(src=(project_path / module), dst=package_path)

    click.secho(f"Editable install of {click.style(project_name,fg='blue',bold=True)} is ready.\n")


if __name__ == '__main__':
    main()