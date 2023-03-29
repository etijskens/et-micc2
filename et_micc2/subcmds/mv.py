import os
from pathlib import Path
# from subprocess import run
from types import SimpleNamespace

import et_micc2.tools.env as env
import et_micc2.tools.messages as messages
import et_micc2.tools.utils as utils

def mv_component(project):
    """Rename, move or remove a component (submodule, Fortran/C++ binary extension module, or app (CLI)."""
    if project.context.msg:
        cmds = [['git', '-a', '-m', project.context.msg]]
        utils.execute(cmds, project.logger.debug, stop_on_error=True)

    p = Path(project.context.component)
    component_traits = SimpleNamespace(
        path=p, name=str(p.name), parent=str(p.parent), to=project.context.to
    )

    # Look up <component> in the project's database to find out what kind of component it is:
    project.deserialize_db()
    try:
        component_traits.db_entry = project.db[str(component_traits.path)]  # may raise KeyError
    except KeyError:
        msg = f"Component '{component_traits.name}' not found."
        # similar = [component for component in env.list_folders_only(project) if (component_traits.to in component)]
        # if similar:
        #     msg +="\nDid you mean:"
        #     for s in similar:
        #         msg += f"\n  - {s} ?"
        messages.error(msg, exit_code=messages.ExitCodes.SUBMODULE_NOT_FOUND.value)

    component_traits.context = component_traits.db_entry['context']
    component_traits.description = (
        'Python submodule'  if component_traits.context['flag_py' ] else
        'Fortran submodule' if component_traits._context['flag_f90'] else
        'C++ submodule'     if component_traits._context['flag_cpp'] else
        'CLI application'   if component_traits._context['flag_cli'] else
        'CLI application (with subcommands)' if component_traits._context['flag_clisub'] else 'oops'
    )
    component_traits.is_cli = component_traits.description.startswith('CLI')

    if component_traits.is_cli:
        if component_traits.to:
            mv_action = rename_component
        else:
            mv_action = remove_component
    else:
        if component_traits.to:
            try:
                to_db_entry = project.db[component_traits.to]
                mv_action = move_component
            except KeyError:
                mv_action = rename_component
        else:
            mv_action = remove_component

    with messages.log(
        project.logger.info,
        f"Package '{project.context.package_name}': "
        f"{mv_action.__name__} {component_traits.description} '{component_traits.path}' -> '{component_traits.to}':"
    ):
        mv_action(project, component_traits)

    del project.db[str(component_traits.path)]
    project.serialize_db()

def rename_component(project, component_traits):
    """"""
    if '/' in component_traits.to:
        messages.error(f"New name must not be path-like: '{component_traits.to}. Specify '{component_traits.name}' instead.")

    package_path = project.context.project_path / project.context.package_name
    package_tests_path = project.context.project_path / 'tests' / project.context.package_name

    if component_traits.is_cli:
        project.replace_in_file(
            package_path / 'cli' / f"{component_traits.name}.py",
            component_traits.name, component_traits.to
        )
        project.replace_in_file(
            package_tests_path / 'cli' / f"test_{component_traits.name}.py",
            component_traits.name, component_traits.to
        )

    else:
        project.replace_in_folder(
            package_path / component_traits.path, component_traits.name, component_traits.to
        )
        project.replace_in_folder(
            package_tests_path / component_traits.path, component_traits.name, component_traits.to
        )

    for key, val in component_traits.db_entry.items():
        if not key == 'context':
            filepath = project.context.project_path / key
            new_string = val.replace(component_traits.name, component_traits.to)
            project.replace_in_file(filepath, val, new_string, contents_only=True)
            component_traits.db_entry[key] = new_string

    # Update the database:
    to_rpath = str( (package_path / component_traits.parent / component_traits.to).relative_to(package_path))
    project.logger.info(f"Updating database entry for : '{to_rpath}'")
    project.db[to_rpath] = component_traits.db_entry


def remove_component(project, component_traits):
    db_component = project.db[component]
    with messages.log(
            project.logger.info,
            f"Package '{project.context.package_name}':  component '{component}' "
            f"Removing {component_type_description} '{component_name}':"
    ):
        if component_type_description.startswith('CLI'):
            project.remove_file(
                project.context.project_path / project.context.package_name / f"{component_name}.py"
            )
            project.remove_file(
                project.context.project_path / 'tests' / project.context.package_name / f"test_{component_name}.py"
            )
        else:
            project.remove_folder(
                project.context.project_path / project.context.package_name / component_name
            )
            project.remove_folder(
                project.context.project_path / 'tests' / project.context.package_name / component_name
            )

        for key, val in db_component.items():
            if not key == 'context':
                path = project.context.project_path / key
                parent_folder, filename, old_string = path.parent, path.name, val
                new_string = ''
                project.replace_in_file(path, old_string, new_string, contents_only=True)

        # Update the database:
        project.logger.info(f"Updating database entry for : '{component}'")

def move_component(project, component_traits):
    """"""