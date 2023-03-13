def doc_cmd(project):
    """Build documentation."""

    if on_vsc_cluster():
        error("The cluster is not suited for building documentation. Use a desktop machine instead.")

    # Check needed tools
    if not ToolInfo('make').is_available():
        error("The make command is missing in your current environment. You must install it to build documentation.")
    if not PkgInfo('sphinx').is_available():
        error("The sphinx package is missing in your current environment.\n"
              "You must install it to build documentation.")
    if not PkgInfo('sphinx_rtd_theme').is_available():
        error("The sphinx_rtd_theme package is missing in your current environment.\n"
              "You must install it to build documentation.")
    if not PkgInfo('sphinx_click').is_available():
        error("The sphinx_click package is missing in your current environment.\n"
              "You must install it to build documentation.")

    project.exit_code = et_micc2.utils.execute(
        ['make', project.context.what],
        cwd=Path(project.context.project_path) / 'docs',
        logfun=project.logger.info
    )
    if project.exit_code:
        error('unexpected error')
