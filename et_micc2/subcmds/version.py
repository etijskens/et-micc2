def version(project):
    """Bump the version according to :py:obj:`project.context.rule` or show the
    current version if no rule is specified.

    The version is stored in pyproject.toml in the project directory, and in
    :py:obj:`__version__` variable of the top-level package, which is either
    in :file:`<package_name>.py`, :file:`<package_name>/__init__.py`, or in
    :file:`<package_name>/__version__.py`.
    """

    # This command does not require any external tools.

    project.context.verbosity = max(1, project.context.verbosity)

    if not project.context.rule:
        if project.context.short:
            print(project.version)
        else:
            click.echo("Project " + click.style(f"({project.context.project_path.name}) ", fg='green')
                       + "version " + click.style(f"({project.version}) ", fg='green')
                       )
    else:
        r = f"--{project.context.rule}"
        current_semver = semantic_version.Version(project.version)
        if project.context.rule == 'patch':
            new_semver = current_semver.next_patch()
        elif project.context.rule == 'minor':
            new_semver = current_semver.next_minor()
        elif project.context.rule == 'major':
            new_semver = current_semver.next_major()
        else:
            r = f"--rule {project.context.rule}"
            new_semver = semantic_version.Version(project.context.rule)

        # update pyproject.toml
        if not project.context.dry_run:
            project.pyproject_toml['tool']['poetry']['version'] = str(new_semver)
            project.pyproject_toml.save()
            # update __version__
            look_for = f'__version__ = "{current_semver}"'
            replace_with = f'__version__ = "{new_semver}"'
            # update in <package_name>/__init__.py
            p = project.context.project_path / project.context.package_name / "__version__.py"
            if p.exists():
                et_micc2.utils.replace_in_file(p, look_for, replace_with)
            else:
                p = project.context.project_path / project.context.package_name / '__init__.py'
                et_micc2.utils.replace_in_file(p, look_for, replace_with)

            project.logger.info(f"({project.context.project_path.name})> version ({current_semver}) -> ({new_semver})")
        else:
            click.echo(f"({project.context.project_path.name})> micc version {r} --dry-run : "
                       + click.style(f"({current_semver} ", fg='cyan') + "-> "
                       + click.style(f"({new_semver})", fg='cyan')
                       )
