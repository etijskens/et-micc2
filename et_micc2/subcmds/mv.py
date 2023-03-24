import os

import et_micc2.tools.env as env
import et_micc2.tools.messages as messages


def mv_component(project):
    """Rename or Remove a component (submodule, sub-package, Fortran module, C++ module, app (CLI)."""
    cur_name, new_name = project.context.cur_name, project.context.new_name
    
    # Look up <cur_name> in the project's database to find out what kind of a component it is:
    project.deserialize_db()
    try:
        db_entry = project.db[cur_name]  # may raise KeyError
    except KeyError:
        msg = f"Submodule '{new_name}' not found."
        similar = [component for component in env.list_folders_only() if (new_name in component)]
        if similar:
            msg +="\nDid you mean:"
            for s in similar:
                msg += f"\n  - {s} ?"
        messages.error(msg, exit_code=messages.ExitCodes.SUBMODULE_NOT_FOUND.value)

    component_context = db_entry['context']
    if new_name:  # rename
            # if project.context.where == 'project':
            #     project.logger.info(f"Replacing all occurrences of '{cur_name}' with '{new_name}' in entire project.")
            #     messages.ask_user_to_continue_or_not()
            #     project.replace_in_folder(project.context.project_path, cur_name, new_name)
            #
            # elif project.context.where == 'package':
            #     project.logger.info(f"Replacing all occurrences of '{cur_name}' with '{new_name}' in entire package.")
            #     project.replace_in_folder(
            #         project.context.project_path / project.context.package_name,
            #         cur_name, new_name
            #     )

        component_type = \
            'Python submodule'  if component_context['flag_py' ] else \
            'Fortran submodule' if component_context['flag_cpp'] else \
            'C++ submodule'     if component_context['flag_cpp'] else \
            'CLI application'   if component_context['flag_cli'] else \
            'CLI application (with subcommands)' if component_context['flag_clisub'] else 'oops'
        if component_type.startswith('CLI'):
            component_name    = f"cli_{cur_name}"
            component_new_name = f"cli_{new_name}"
        else:
            component_name    = cur_name
            component_new_name = new_name

        with messages.log(
                project.logger.info,
                f"Package '{project.context.package_name}': "
                f"Renaming {component_type} '{component_name}' -> '{component_new_name}':"
            ):
            if component_type.startswith('CLI'):
                project.replace_in_file(
                    project.context.project_path / project.context.package_name / f"{component_name}.py",
                    cur_name, new_name
                )
                project.replace_in_file(
                    project.context.project_path / 'tests' / project.context.package_name / f"test_{component_name}.py",
                    cur_name, new_name
                )
            else:
                project.replace_in_folder(
                    project.context.project_path / project.context.package_name / component_name,
                    cur_name, new_name
                )
                project.replace_in_folder(
                    project.context.project_path / 'tests' / project.context.package_name,
                    cur_name, new_name
                )

            for key, val in db_entry.items():
                if not key == 'context':
                    filepath = project.context.project_path / key
                    new_string = val.replace(cur_name, new_name)
                    project.replace_in_file(filepath, val, new_string, contents_only=True)
                    db_entry[key] = new_string

            # Update the database:
            project.logger.info(f"Updating database entry for : '{cur_name}'")
            project.db[new_name] = db_entry

    else:  # remove
        with messages.log(project.logger.info
                , f"Package '{project.context.package_name}' Removing component '{cur_name}'"
                                 ):
            if component_context['package']:
                project.logger.info(f"Removing Python sub-package: '{cur_name}{os.sep}__init__.py'")
                project.remove_folder(project.context.project_path / project.context.package_name / cur_name)
                project.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_{cur_name}.py', )

            elif component_context['py']:
                project.logger.info(f"Removing Python submodule: '{cur_name}.py'")
                project.remove_file(project.context.project_path / project.context.package_name / f'{cur_name}.py')
                project.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_{cur_name}.py')

            elif component_context['f90']:
                project.logger.info(f"Removing Fortran submodule: 'f90_{cur_name}")
                project.remove_folder(project.context.project_path / project.context.package_name / f'f90_{cur_name}')
                project.logger.info(f"Removing test file: 'tests/test_f90_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_f90_{cur_name}.py')

            elif component_context['cpp']:
                project.logger.info(f"Removing C++ submodule: 'cpp_{cur_name}")
                project.remove_folder(project.context.project_path / project.context.package_name / f'cpp_{cur_name}')
                project.logger.info(f"Removing test file: 'tests/test_cpp_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_cpp_{cur_name}.py')

            elif component_context['cli'] or component_context['clisub']:
                project.logger.info(f"Removing CLI: 'cli_{cur_name}.py'")
                project.remove_file(project.context.project_path / project.context.package_name / f"cli_{cur_name}.py")
                project.logger.info(f"Removing test file: 'test_cli_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f"test_cli_{cur_name}.py")

            for key, val in db_entry.items():
                if not key == 'context':
                    path = project.context.project_path / key
                    parent_folder, filename, old_string = path.parent, path.name, val
                    new_string = ''
                    project.replace_in_file(path, old_string, new_string, contents_only=True)

            # Update the database:
            project.logger.info(f"Updating database entry for : '{cur_name}'")

    del project.db[cur_name]
    project.serialize_db()
