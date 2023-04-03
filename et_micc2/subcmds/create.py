import os
from pathlib import Path
import re
import requests
import subprocess

import et_micc2.tools.config as config
import et_micc2.tools.env as env
import et_micc2.tools.expand as expand
import et_micc2.tools.messages as messages
import et_micc2.tools.utils as utils
import et_micc2.tools.project

def create(project):
    """Create a new project skeleton."""

    # Check for tools needed:
    # . git is required for creating a local repo
    # . gh is required for creating a remote repo

    if project.context.project_path.exists() and os.listdir(str(project.context.project_path)):
        messages.error(
            f"Cannot create project in ({project.context.project_path}):\n"
            f"  Directory must be empty."
        )

    toolinfo_git = env.ToolInfo('git')
    if not project.context.no_git and not toolinfo_git.is_available():
        if env.on_vsc_cluster():
            messages.warning(
                'Your current environment has no suitable git command.\n'
                'Load a cluster module that has git.\n'
                'If you continue, this project will NOT have a local git repository.'
            )
        else:
            messages.warning(
                'Your current environment has no git command.\n'
                'To install git: https://git-scm.com/downloads.\n'
                'If you continue, this project will NOT have a local git repository.'
            )
        if project.context.silent:
            messages.error("Git is missing. Project not created.", exit_code=env.ExitCodes.MISSING_COMPONENT.value)
        else:
            messages.ask_user_to_continue_or_not(stop_message="Git is missing. Project not created.")

    if project.context.github_repo != 'none':
        # Check that we have github username
        github_username = project.context.template_parameters['github_username']
        if not github_username:
            messages.error(
                'Micc2 configuration does not have a github username. Creation of remote repo is not possible.\n'
                'Project is not created.'
            )
        # Check availability of gh command:
        if not env.ToolInfo('gh').is_available() and project.context.github_repo:
            messages.warning(
                'The gh command is not available in your environment.\n'
                'If you continue this project a remote repository will not be created.'
            )
            messages.ask_user_to_continue_or_not(stop_message='Project not created.')

    if not project.context.allow_nesting:
        # Prevent the creation of a project inside another project
        p = project.context.project_path.parent.resolve()
        while not p.samefile(os.sep):
            if et_micc2.tools.project.is_project_directory(p):
                messages.error(
                    f"Cannot create project in ({project.context.project_path}):\n"
                    f"  Specify '--allow-nesting' to create a et_micc2 project inside another et_micc2 project ({p})."
                )
            p = p.parent

    # Proceed creating the project
    project.context.project_path.mkdir(parents=True, exist_ok=True)

    if not project.context.module_name:
        # derive package name from project name
        if not utils.verify_project_name(project.context.project_path.name):
            messages.error(
                f"The project name ({project.context.project_path.name}) does not yield a PEP8 compliant module name:\n"
                f"  The project name must start with char, and contain only chars, digits, hyphens and underscores.\n"
                f"  Alternatively, provide an explicit module name with the --module-name=<name>."
            )
        else:
            project.context.package_name = utils.pep8_module_name(project.context.project_path.name)
    else:
        project.context.package_name = project.context.module_name

    try:
        relative_project_path = project.context.project_path.relative_to(Path.cwd())
    except ValueError:
        # project_path was specified relative to cwd using ../
        # use full path instead of relative path
        relative_project_path = project.context.project_path

    if project.context.publish:
        rv = utils.existsOnPyPI(project.context.package_name)
        if rv is False:
            pass  # the name is not yet in use
        else:
            if rv is True:
                messages.error(
                    f"    The name '{project.context.package_name}' is already in use on PyPI.\n"
                    f"    The project is not created.\n"
                    f"    You must choose another name if you want to publish your code on PyPI."
                )
            elif isinstance(rv, requests.exceptions.ConnectionError):
                messages.error(f"    ConnectionError: Check your internect connection.\n"
                      f"    The availability of name '{project.context.package_name}' on PyPI could not be verified. \n"
                      f"    The project is not created."
                      )
            else:  # unknown error
                messages.error(
                    f"    {type(rv)}\n"
                    f"    {str(rv)}\n"
                    f"    The availability of name '{project.context.package_name}' on PyPI could not be verified. \n"
                    f"    The project is not created."
                )

    source_file = str(relative_project_path / project.context.package_name / '__init__.py')

    project.context.verbosity = max(1, project.context.verbosity)

    # The project directory is created, so we can get ourselves a logger:
    project.get_logger()

    with messages.logtime(project):
        with messages.log( project.logger.info
                         , f"Creating project directory ({project.context.project_path.name}):"
                         ):
            project.logger.info(f"Python top-level package ({project.context.package_name}):")

            # project_name must come before package_name because the value of package_name depends on project_name
            template_parameters = config.Config( project_name=project.context.project_path.name
                                               , package_name=project.context.package_name
                                               )
            template_parameters.update(project.context.template_parameters.data)
            project.context.template_parameters = template_parameters

            project.context.overwrite = False
            msg = expand.expand_templates(project.context)
            if msg:
                project.logger.critical(msg)
                project.logger.info(f'Cleaning up after failure...')
                # Remove the project directory
                project.context.project_path.unlink()
                return

            proj_cfg = project.context.project_path / 'micc3.cfg'
            project.context.template_parameters.save(proj_cfg)

            # add git support if requested
            if project.context.no_git:
                project.logger.warning(
                    f"Flag `--no-git` specified: project `{project.context.project_path.name}` created without git support."
                )
            else:
                with messages.log(project.logger.info, "Creating local git repository"):
                    with utils.in_directory(project.context.project_path):
                        vs = toolinfo_git.version()
                        re_git_version = re.compile('^git version (\d+\.\d*\.\d*).*')
                        m = re_git_version.match(vs)
                        git_Mmp = m[1]
                        # print(git_Mmp)
                        if git_Mmp > '2.30':
                            cmds = [['git', 'init',
                                     f'--initial-branch={project.context.template_parameters["git_default_branch"]}']
                                    ]
                        else:
                            cmds = [['git', 'init']
                                    ]
                        cmds.extend(
                            [ ['git', 'add', '*']
                            , ['git', 'add', '.gitignore']
                            , ['git', 'commit', '-m', f'"Initial commit from `micc2 create {project.context.project_path.name}`"']
                            ]
                        )

                        returncode = utils.execute(cmds, project.logger.debug, stop_on_error=True)
                if not returncode:
                    if project.context.github_repo:
                        # todo this context manager does not print correctly
                        with messages.log(
                                project.logger.info,
                                f"Creating {project.context.github_repo} remote git repository at "
                                f"git://github.com/{github_username}/{project.context.project_path.name}"
                        ):
                            with utils.in_directory(project.context.project_path):
                                pat_file = project.context._cfg_dir / f'{project.context.template_parameters["github_username"]}.pat'
                                if pat_file.exists():
                                    with open(pat_file) as f:
                                        completed_process = \
                                            subprocess.run(['gh', 'auth', 'login', '--with-token'], stdin=f, text=True)
                                        utils.log_completed_process(completed_process, project.logger.debug)
                                        cmd = ['gh', 'repo', 'create'
                                            , '--source', str(project.context.project_path)
                                            , f'--{project.context.github_repo}'  # --private or --public
                                            , '--push'  # push the contents
                                               ]
                                        utils.execute(cmd, project.logger.debug, stop_on_error=True)
                                else:
                                    project.logger.messages.error(
                                        f"Unable to access your GitHub account: \n"
                                        f"    Personal access token not found: '{pat_file}'.\n"
                                        f"Remote repository not created."
                                    )
                    else:
                        project.logger.warning("Creation of remote GitHub repository not requested.")

            # project.logger.warning(
            #     "Run 'poetry install' in the project directory to create a virtual "
            #     "environment and install its dependencies."
            # )

    if project.context.publish:
        project.logger.warning(
            f"The name '{project.context.package_name}' is still available on PyPI.\n"
            "To claim the name, it is best to publish your project right away\n"
            "by running 'poetry publish --build'."
        )
