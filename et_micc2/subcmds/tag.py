def tag(project):
    """Create and push a version tag ``v<Major>.<minor>.<patch>`` for the current version."""

    # Git is required

    git = ToolInfo('git')
    if not git.is_available():
        s = '(or not suitable) ' if on_vsc_cluster() else ''
        error(f'The tag command requires git, which is not available {s}in your environment.\n'
              'Exiting.')

    tag = f"v{project.version}"

    with et_micc2.utils.in_directory(project.context.project_path):
        project.logger.info(f"Creating git tag {tag} for project {project.context.project_path.name}")
        cmd = ['git', 'tag', '-a', tag, '-m', f'"tag version {project.version}"']
        project.logger.debug(f"Running '{' '.join(cmd)}'")
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        project.logger.debug(completed_process.stdout.decode('utf-8'))
        if completed_process.stderr:
            project.logger.critical(completed_process.stderr.decode('utf-8'))

        project.logger.debug(f"Pushing tag {tag} for project {project.context.project_path.name}")
        cmd = ['git', 'push', 'origin', tag]
        project.logger.debug(f"Running '{' '.join(cmd)}'")
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if completed_process.returncode == 0:
            if completed_process.stdout:
                project.logger.debug(completed_process.stdout.decode('utf-8'))
        else:
            if completed_process.stdout:
                project.logger.warning(completed_process.stdout.decode('utf-8'))
            if completed_process.stderr:
                project.logger.warning(completed_process.stderr.decode('utf-8'))
            project.logger.warning(f"Failed '{' '.join(cmd)}'\nRerun the command later (you must be online).")

    project.logger.info('Done.')
