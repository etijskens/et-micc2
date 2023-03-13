__pybind11_required_version__ = '2.6.2'

def build_cmd(project):
    """Build a binary extension."""

    # Exit if cmake is not available:
    if not ToolInfo('cmake').is_available():
        msg = 'The build command requires cmake, which is not available in your current environment.\n'
        if on_vsc_cluster():
            msg += 'Load a cluster module that enables cmake.'
        else:
            msg += 'Make sure cmake is installed and on your PATH.'
        error(msg)

    # get extension for binary extensions (depends on OS and python version)
    extension_suffix = get_extension_suffix()

    package_path = project.context.project_path / project.context.package_name

    build_options = project.context.build_options
    if build_options.module_to_build:
        build_options.module_to_build = package_path / build_options.module_to_build

    succeeded = []
    failed = []
    for root, dirs, files in os.walk(package_path):
        for dir in dirs:
            p_root = Path(root)
            submodule_type = get_submodule_type(p_root / dir)
            # print(root, dir,submodule_type)
            if submodule_type in ('f90', 'cpp'):
                build = True
                if build_options.module_to_build:
                    if build_options.module_to_build != p_root / dir:
                        build = False
                if build:
                    if submodule_type == 'f90':
                        # Exit if f2py is not available
                        if not ToolInfo('f2py').is_available():
                            msg = 'Building a Fortran binary extension requires f2py, which is not available in your current environment.\n' \
                                  '(F2py is part of the numpy Python package).'
                            if on_vsc_cluster():
                                msg += 'Load a cluster module that has the numpy package pre-installed.'
                            else:
                                msg += 'If you are using a virtual environment, install numpy as:\n' \
                                       '    (.venv) > pip install numpy\n' \
                                       'otherwise,\n' \
                                       '    > pip install numpy --user\n'
                            error(msg)
                    elif submodule_type == 'cpp':
                        # exit if pybind11 is not available, and warn if too old...
                        pybind11 = PkgInfo('pybind11')
                        if not pybind11.is_available():
                            error(
                                'Building C++ binary extensions requires pybind11, which is not available in your current environment.\n'
                                'If you are using a virtual environment, install it as .\n'
                                '    (.venv) > pip install pybind11\n'
                                'otherwise,\n'
                                '    > pip install pybind11 --user\n'
                                , exit_code=_exit_missing_component
                            )
                        else:
                            if pybind11.version() < __pybind11_required_version__:
                                warning(
                                    f'Building C++ binary extensions requires pybind11, which is available in your current environment (v{pybind11.version()}).\n'
                                    f'However, you may experience problems because it is older than v{__pybind11_required_version__}.\n'
                                    'Upgrading is recommended.'
                                )

                    build_options.submodule_srcdir_path = build_options.module_to_build if build_options.module_to_build else (
                                p_root / dir)
                    build_options.submodule_path = build_options.submodule_srcdir_path.parent
                    build_options.submodule_name = build_options.submodule_srcdir_path.name
                    build_options.submodule_binary = build_options.submodule_path / (
                                build_options.submodule_name + extension_suffix)
                    build_options.submodule_type = submodule_type

                    if build_binary_extension(project.context):
                        failed.append(build_options.submodule_binary)
                    else:
                        succeeded.append(build_options.submodule_binary)

    if succeeded:
        project.logger.info("\n\nBinary extensions built successfully:")
        for binary_extension in succeeded:
            project.logger.info(f"  - {binary_extension}")

    if failed:
        project.logger.error("\nBinary extensions failing to build:")
        for binary_extension in failed:
            project.logger.error(f"  - {binary_extension}")

    if not succeeded and not failed:
        warning(f"No binary extensions found in package ({project.context.package_name}).")


def build_binary_extension(context):
    """Build a binary extension described by *context*.

    :param context:
    :return:
    """
    build_options = context.build_options

    # Remove so file to avoid "RuntimeError: Symlink loop from ..."
    try:
        build_options.submodule_binary.unlink()  # missing_ok=True only available from 3.8 on, not in 3.7
    except FileNotFoundError:
        pass
    module_to_build = build_options.submodule_srcdir_path.relative_to(context.project_path)
    build_log_file = build_options.submodule_srcdir_path / "micc-build.log"
    build_logger = et_micc2.logger.create_logger(build_log_file, filemode='w')
    with et_micc2.logger.log(build_logger.info, f"Building {build_options.submodule_type} module '{module_to_build}':"):
        destination = build_options.submodule_binary

        if build_options.submodule_type in ('cpp', 'f90') and (build_options.submodule_srcdir_path / 'CMakeLists.txt').is_file():
            output_dir = build_options.submodule_srcdir_path / '_cmake_build'
            # build_dir = output_dir
            if build_options.clean and output_dir.exists():
                build_logger.info(f"--clean: shutil.removing('{output_dir}').")
                shutil.rmtree(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            with et_micc2.utils.in_directory(output_dir):
                cmake_cmd = ['cmake', '-D', f"PYTHON_EXECUTABLE={sys.executable}"]
                # CAVEAT: using sys.executable implies that we automatically build against the python version used
                #         by micc2. This is not always what we want.
                for key,val in context.build_options.cmake.items():
                    cmake_cmd.extend(['-D', f"{key}={val}"])
                if sys.platform == 'win32':
                    cmake_cmd.extend(['-G', 'NMake Makefiles'])
                    make = 'nmake'
                else:
                    make = 'make'

                if build_options.submodule_type== 'cpp':
                    cmake_cmd.extend(['-D', f"pybind11_DIR={path_to_cmake_tools()}"])

                cmake_cmd.append('..')

                cmds = [ cmake_cmd
                       , [make, 'VERBOSE=1']
                       # [make, 'install']
                ]
                # This is a fix for the native Windows case, when using the
                # Intel Python distribution and building a f90 binary extension
                fix = sys.platform == 'win32' and 'intel' in sys.executable and context.module_kind == 'f90'
                if not fix:
                    cmds.append([make, 'install'])

                exit_code = et_micc2.utils.execute(
                    cmds, build_logger.debug, stop_on_error=True, env=os.environ.copy()
                )

                if fix:
                    from glob import glob
                    search = str(build_options.submodule_srcdir_path / '_cmake_build' / f'{context.module_name}.*.pyd')
                    # print(search)
                    pyd = glob(search)
                    dst = build_options.submodule_binary.parent / f'{build_options.submodule_name}.pyd'
                    build_logger.info(f'Installing `{pyd[0]}` as {dst}')
                    shutil.copyfile(pyd[0], dst)

                if build_options.cleanup:
                    build_logger.info(f"--cleanup: shutil.removing('{output_dir}').")
                    shutil.rmtree(build_dir)
        else:
            raise RuntimeError("Bad submodule type, or no CMakeLists.txt   ")

    return exit_code


def path_to_cmake_tools():
    """Return the path to the folder with the CMake tools.

    """
    found = ''
    # look in global site-packages:
    site_packages = site.getsitepackages()
    site_packages.append(site.getusersitepackages())
    print(site_packages)
    for d in site_packages:
        pd = Path(d) / 'pybind11'
        if pd.exists():
            found = pd
            break

    if not found:
        raise ModuleNotFoundError('pybind11 not found in {site_packages}')

    p = pd / 'share' / 'cmake' / 'pybind11'
    print(f'path_to_cmake_tools={p}')
    return str(p)


def get_extension_suffix():
    """Return the extension suffix, e.g. :file:`.cpython-37m-darwin.so`."""
    return sysconfig.get_config_var('EXT_SUFFIX')


def auto_build_binary_extension(package_path, module_to_build):
    """

    :param Path package_path:
    :param str module_to_build:
    :return: exit_code
    """
    options = SimpleNamespace( package_path  = package_path
                             , verbosity     = 1
                             , module_name   = module_to_build
                             , build_options = SimpleNamespace( module_to_build = module_to_build
                                                              , clean           = True
                                                              , cleanup         = True
                                                              , cmake           = {'CMAKE_BUILD_TYPE': 'RELEASE'}
                                                              )
                             )
    for module_prefix in ["cpp", "f90"]:
        module_srcdir_path = package_path / f"{module_prefix}_{context.module_name}"
        if module_srcdir_path.exists():
            context.module_kind = module_prefix
            context.module_srcdir_path = module_srcdir_path
            context.build_options.build_tool_options = {}
            break
    else:
        raise ValueError(f"No binary extension source directory found for module '{module_to_build}'.")

    exit_code = build_binary_extension(options)

    msg = ("[ERROR]\n"
          F"    Binary extension module '{context.module_name}{get_extension_suffix()}' could not be build.\n"
           "    Any attempt to use it will raise exceptions.\n"
           ) if exit_code else ""
    return msg
