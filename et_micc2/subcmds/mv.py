import os
from pathlib import Path
from subprocess

import et_micc2.tools.env as env
import et_micc2.tools.messages as messages
import et_micc2.tools.utils as utils

def mv_component(project):
    """Rename, move or remove a component (submodule, Fortran/C++ binary extension module, or app (CLI)."""
    component, destination = project.context.component, project.context.destination

    if project.context.msg:
        cmds = [['git', '-a', '-m', project.context.msg]]
        utils.execute(cmds, project.logger.debug, stop_on_error=True)

    # Look up <component> in the project's database to find out what kind of component it is:
    project.deserialize_db()
    try:
        db_component = project.db[component]  # may raise KeyError
    except KeyError:
        msg = f"Submodule '{component}' not found."
        similar = [component for component in env.list_folders_only() if (destination in component)]
        if similar:
            msg +="\nDid you mean:"
            for s in similar:
                msg += f"\n  - {s} ?"
        messages.error(msg, exit_code=messages.ExitCodes.SUBMODULE_NOT_FOUND.value)

    component_context = db_component['context']
    component_type_description = \
        'Python submodule'  if component_context['flag_py' ] else \
        'Fortran submodule' if component_context['flag_f90'] else \
        'C++ submodule'     if component_context['flag_cpp'] else \
        'CLI application'   if component_context['flag_cli'] else \
        'CLI application (with subcommands)' if component_context['flag_clisub'] else 'oops'

    mv_args = {
        'project' : project,
        'component_context' : component_context,
    }

    if component_type_description.startswith('CLI'):
        component_name = f"cli_{component}"
        if destination:
            mv_action = rename_component
            component_new_name = f"cli_{destination}"
        else:
            mv_action = remove_component
    else:
        component_name = component
        if destination:
            component_new_name = destination
            try:
                dest_db_entry = project.db[destination]
                mv_action = move_component
            except KeyError:
                mv_action = rename_component
        else:
            mv_action = remove_component

    with messages.log(
        project.logger.info,
        f"Package '{project.context.package_name}': "
        f"{mv_action.func_name} {component_type_description} '{component_name}' -> '{component_new_name}':"
    ):
        mv_action(project, component, component_name, component_type_description, component_new_name)

    del project.db[component]
    project.serialize_db()

def rename_component(project, component, component_name, component_type_description, component_new_name):
    if component_type_description.startswith('CLI'):
        project.replace_in_file(
            project.context.project_path / project.context.package_name / f"{component_name}.py",
            component, destination
        )
        project.replace_in_file(
            project.context.project_path / 'tests' / project.context.package_name / f"test_{component_name}.py",
            component, destination
        )
    else:
        if '/' in destination:
            messages.error(f"new name must not be path-like: '{destination}. Change to {Path(destination).name}'.")

        project.replace_in_folder(
            project.context.project_path / project.context.package_name / component_name,
            destination
        )
        project.replace_in_folder(
            project.context.project_path / 'tests' / project.context.package_name / component_name,
            destination
        )

    for key, val in db_component.items():
        if not key == 'context':
            filepath = project.context.project_path / key
            new_string = val.replace(component, destination)
            project.replace_in_file(filepath, val, new_string, contents_only=True)
            db_component[key] = new_string

    # Update the database:
    project.logger.info(f"Updating database entry for : '{component}'")
    project.db[str(Path(component).parent / destination)] = db_component


def remove_component(project, component, component_name, component_type_description):
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

def move_component()