def mv_component(project):
    """Rename or Remove a component (submodule, sub-package, Fortran module, C++ module, app (CLI)."""
    cur_name, new_name = project.context.cur_name, project.context.new_name
    # Look up <cur_name> in the project's database to find out what kind of a component it is:
    project.deserialize_db()
    db_entry = project.db[cur_name]  # may raise KeyError

    component_options = db_entry['context']
    if new_name:  # rename
        with et_micc2.logger.log(project.logger.info
                , f"Package '{project.context.package_name}' Renaming component {cur_name} -> {new_name}:"
                                 ):
            if project.context.entire_project:
                project.logger.info(f"Renaming entire project (--entire-project): '{project.context.project_path.name}'")
                project.replace_in_folder(project.context.project_path, cur_name, new_name)

            elif project.context.entire_package:
                project.logger.info(f"Renaming entire package (--entire-package): '{project.context.package_name}'")
                project.replace_in_folder(project.context.project_path / project.context.package_name, cur_name, new_name)

            elif component_options['package']:
                project.logger.info(f"Renaming Python sub-package: '{cur_name}{os.sep}__init__.py'")
                project.replace_in_folder(project.context.project_path / project.context.package_name / cur_name, cur_name,
                                       new_name)
                project.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                project.replace_in_file(project.context.project_path / 'tests' / f'test_{cur_name}.py', cur_name, new_name)

            elif component_options['py']:
                project.logger.info(f"Renaming Python submodule: '{cur_name}.py'")
                project.replace_in_file(project.context.project_path / project.context.package_name / f'{cur_name}.py', cur_name,
                                     new_name)
                project.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                project.replace_in_file(project.context.project_path / 'tests' / f'test_{cur_name}.py', cur_name, new_name)

            elif component_options['f90']:
                project.logger.info(f"Fortran submodule: 'f90_{cur_name}{os.sep}{cur_name}.f90'")
                project.replace_in_folder(project.context.project_path / project.context.package_name / f'f90_{cur_name}',
                                       cur_name, new_name)
                project.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                project.replace_in_file(project.context.project_path / 'tests' / f'test_f90_{cur_name}.py', cur_name,
                                     new_name)

            elif component_options['cpp']:
                project.logger.info(f"C++ submodule: 'cpp_{cur_name}{os.sep}{cur_name}.cpp'")
                project.replace_in_folder(project.context.project_path / project.context.package_name / f'cpp_{cur_name}',
                                       cur_name, new_name)
                project.logger.info(f"Renaming test file: 'tests/test_{cur_name}.py'")
                project.replace_in_file(project.context.project_path / 'tests' / f'test_cpp_{cur_name}.py', cur_name,
                                     new_name)

            elif component_options['app'] or component_options['group']:
                project.logger.info(f"Command line interface (no subcommands): 'cli_{cur_name}.py'")
                project.replace_in_file(project.context.project_path / project.context.package_name / f"cli_{cur_name}.py",
                                     cur_name, new_name)
                project.replace_in_file(project.context.project_path / 'tests' / f"test_cli_{cur_name}.py", cur_name,
                                     new_name)

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
        with et_micc2.logger.log(project.logger.info
                , f"Package '{project.context.package_name}' Removing component '{cur_name}'"
                                 ):
            if component_options['package']:
                project.logger.info(f"Removing Python sub-package: '{cur_name}{os.sep}__init__.py'")
                project.remove_folder(project.context.project_path / project.context.package_name / cur_name)
                project.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_{cur_name}.py', )

            elif component_options['py']:
                project.logger.info(f"Removing Python submodule: '{cur_name}.py'")
                project.remove_file(project.context.project_path / project.context.package_name / f'{cur_name}.py')
                project.logger.info(f"Removing test file: 'tests/test_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_{cur_name}.py')

            elif component_options['f90']:
                project.logger.info(f"Removing Fortran submodule: 'f90_{cur_name}")
                project.remove_folder(project.context.project_path / project.context.package_name / f'f90_{cur_name}')
                project.logger.info(f"Removing test file: 'tests/test_f90_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_f90_{cur_name}.py')

            elif component_options['cpp']:
                project.logger.info(f"Removing C++ submodule: 'cpp_{cur_name}")
                project.remove_folder(project.context.project_path / project.context.package_name / f'cpp_{cur_name}')
                project.logger.info(f"Removing test file: 'tests/test_cpp_{cur_name}.py'")
                project.remove_file(project.context.project_path / 'tests' / f'test_cpp_{cur_name}.py')

            elif component_options['cli'] or component_options['clisub']:
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
