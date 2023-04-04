import os
import shutil
from pathlib import Path
# from subprocess import run
from types import SimpleNamespace
from typing import Union

import et_micc2.tools.env as env
import et_micc2.tools.messages as messages
import et_micc2.tools.utils as utils

def mv(project):
    """Rename, move or remove a component (submodule, Fortran/C++ binary extension module, or app (CLI)."""
    with utils.in_directory(project.context.project_path):
        if project.context.commit_msg:
            cmds = [['git', 'commit', '-a', '-m', project.context.commit_msg]]
            utils.execute(cmds, project.logger.debug, stop_on_error=True)

    p = Path(project.context.component)
    component_traits = SimpleNamespace(
        path=p, name=str(p.name), parent=str(p.parent), to=project.context.to
    )

    # Look up <component> in the project's database to find out what kind of component it is:
    try:
        component_traits.db_entry = project.components[str(component_traits.path)]  # may raise KeyError
    except KeyError:
        msg = f"Component '{component_traits.name}' not found."
        similar = project.components.similar_to(component_traits.name)
        if similar:
            msg +="\nDid you mean:"
            for s in similar:
                msg += f"\n  - {s} ?"
        messages.error(msg, exit_code=messages.ExitCodes.SUBMODULE_NOT_FOUND.value)

    component_traits.context = component_traits.db_entry['context']
    component_traits.description = (
        'Python submodule'  if component_traits.context['flag_py' ] else
        'Fortran submodule' if component_traits.context['flag_f90'] else
        'C++ submodule'     if component_traits.context['flag_cpp'] else
        'CLI application'   if component_traits.context['flag_cli'] else
        'CLI application (with subcommands)' if component_traits._context['flag_clisub'] else 'oops'
    )
    component_traits.is_cli = component_traits.description.startswith('CLI')

    if component_traits.is_cli:
        # CLIs can't be moved
        if component_traits.to:
            mv_action = mv_rename
        else:
            mv_action = mv_remove
    else:
        if component_traits.to:
            if component_traits.to in project.components:
                mv_action = mv_move
            else:
                mv_action = mv_rename
        else:
            mv_action = mv_remove

    with messages.log(
        project.logger.info,
        f"Package '{project.context.package_name}': "
        f"{mv_action.__name__} {component_traits.description} '{component_traits.path}' -> '{component_traits.to}':"
    ):
        to_entry = mv_action(project, component_traits)

    # Update the database:
    del project.components[str(component_traits.path)]
    project.serialize(new_components=to_entry)


def mv_rename(project, component_traits):
    """"""
    if '/' in component_traits.to:
        messages.error(f"New name must not be path-like: '{component_traits.to}. Specify '{component_traits.name}' instead.")

    package_path = project.context.project_path / project.context.package_name
    package_tests_path = project.context.project_path / 'tests' / project.context.package_name

    if component_traits.is_cli:
        project.replace_in_file(
            package_path / 'cli' / f"{component_traits.name}.py",
            [(component_traits.name, component_traits.to)]
        )
        project.replace_in_file(
            package_tests_path / 'cli' / f"test_{component_traits.name}.py",
            [(component_traits.name, component_traits.to)]
        )

    else:
        project.replace_in_folder(
            package_path / component_traits.path, [(component_traits.name, component_traits.to)]
        )
        project.replace_in_folder(
            package_tests_path / component_traits.path, [(component_traits.name, component_traits.to)]
        )

    for key, val in component_traits.db_entry.items():
        if key == 'context':
            context = component_traits.db_entry[key]
            for k,v in context.items():
                if isinstance(v, str):
                    v2 = v.replace(component_traits.name, component_traits.to)
                    if v2 != v:
                        context[k] = v2
        else:
            filepath = project.context.project_path / key
            new_string = val.replace(component_traits.name, component_traits.to)
            project.replace_in_file(filepath, [(val, new_string)], contents_only=True)
            component_traits.db_entry[key] = new_string


    return component_traits.db_entry


def mv_remove(project, component_traits):
    """"""
    package_path = project.context.project_path / project.context.package_name
    package_tests_path = project.context.project_path / 'tests' / project.context.package_name

    if component_traits.is_cli:
        project.remove_file(package_path       / 'cli' / f"{component_traits.name}.py")
        project.remove_file(package_tests_path / 'cli' / f"{component_traits.name}.py")
    else:
        project.remove_folder(package_path       / component_traits.path)
        project.remove_folder(package_tests_path / component_traits.path)

    for key, val in component_traits.db_entry.items():
        if not key == 'context':
            path = project.context.project_path / key
            parent_folder, filename, old_string = path.parent, path.name, val
            new_string = ''
            project.replace_in_file(path, [(old_string, new_string)], contents_only=True)

    return None 
    #   Since the component is removed, there is no db_entry to return


def mv_move(project, component_traits):
    """"""
    try:
        project.components[component_traits.path]
    except KeyError:
        messages.error(f"Inexisting source: '{component_traits.path}'.")

    try:
        project.components[component_traits.to] # may raise KeyError, which implies a rename and a move
        # if no KeyError is raised, perform only a move
        after_rename = False
    except KeyError:
        # this is a move with a rename. First perform the rename, then the move
        to_path = component_traits.to
        to_name = Path(component_traits.to).name
        try:
            to_parent = Path(to_path).parent
            project.components[to_parent] # may raise KeyError
        except KeyError:
            messages.error(f"Destination {to_parent} does not exist.")

        # prepare for renaming
        project.context.to = to_name
        commit_msg = project.context.commit_msg
        project.context.commit_msg = '' # we don't want separate commits for the rename and the move
        mv(project) # rename
        # prepare for moving
        component_traits.to = Path(to_path).parent
        component_traits.path = Path(project.context.component).parent / to_name
        after_rename = True

    # Perform the move
    package_path      = project.context.project_path / project.context.package_name
    package_test_path = project.context.project_path / 'tests' / project.context.package_name
    shutil.move(package_path / component_traits.path, package_path / component_traits.to)

    package_name = package_path.name
    paths = [component_traits.path, component_traits.to]
    with utils.in_directory(package_path):
        common_path = env.common_path(paths)
        pr = [Path(p).resolve().relative_to(common_path) for p in paths]
        pr[1] = pr[1] / component_traits.name
        import_libs = [str(p).replace(os.sep, '.') for p in pr]
    replace = [
        (import_libs[0], import_libs[1]),
    ]
    project.replace_in_folder(package_path, replace)
    project.replace_in_folder(package_test_path, replace)

    db_entry = component_traits.db_entry
    for key, val in db_entry.items():
        if key == 'context':
            context = component_traits.db_entry[key]
            context['add_name'] = str(Path(component_traits.to) / component_traits.name)
            context['module_srcdir'] = str(Path(context['package_name']) / context['add_name'])
            context['import_lib'] = context['module_srcdir'].replace(os.sep, '.')
        else:
            path = project.context.project_path / key
            parent_folder, filename, old_string = path.parent, path.name, val
            new_string = ''
            project.replace_in_file(path, [(old_string, new_string)], contents_only=True)

    if after_rename:
        # restore the commit message in the component database
        db_entry['context']['commit_msg'] = commit_msg

    return db_entry

