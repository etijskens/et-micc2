from pathlib import Path
import et_micc2.tools.env as env
import et_micc2.tools.messages as messages
import et_micc2.tools.utils as utils

def doc(project):
    """Build documentation."""

    if env.on_vsc_cluster():
        messages.error(
            "The cluster is not suited for building documentation. Use a desktop machine instead.",
            exit_code=messages.ExitCodes.RuntimeError
        )

    # Check needed tools
    if not env.ToolInfo('make').is_available():
        messages.error(
            "The make command is missing in your current environment. You must install it to build documentation.",
            exit_code=messages.ExitCodes.RuntimeError.value
            )
    if not env.PkgInfo('sphinx').is_available():
        messages.error(
            "The sphinx package is missing in your current environment.\n"
            "You must install it to build documentation.",
            exit_code=messages.ExitCodes.RuntimeError.value
        )
    if not env.PkgInfo('sphinx_rtd_theme').is_available():
        messages.error(
            "The sphinx_rtd_theme package is missing in your current environment.\n"
            "You must install it to build documentation.",
            exit_code=messages.ExitCodes.RuntimeError.value
        )
    if not env.PkgInfo('sphinx_click').is_available():
        messages.error(
            "The sphinx_click package is missing in your current environment.\n"
            "You must install it to build documentation.",
            exit_code=messages.ExitCodes.RuntimeError.value
        )

    project.exit_code = utils.execute(
        ['make', project.context.what],
        cwd=Path(project.context.project_path) / 'docs',
        logfun=project.logger.info
    )
    if project.exit_code:
        messages.error('unexpected error')
