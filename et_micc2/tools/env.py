import os
import pkg_resources
import shutil
import subprocess


def on_vsc_cluster():
    """test if we are running on one of the VSC clusters"""
    try:
        os.environ['VSC_HOME']
        os.environ['VSC_INSTITUTE_CLUSTER']
    except:
        return False
    else:
        return True


def is_os_tool(path_to_exe):
    """test if path_to_exe was installed as part of the OS."""
    return path_to_exe.startswith('/usr/bin')


class PkgInfo:
    mock = [] # list of module names to pretend missing. This is just for testing purposes.

    def __init__(self, pkg_name):
        if pkg_name in PkgInfo.mock:
            print(f'Mock: pretending module `{pkg_name}` is missing.')
            self.which = ''
        else:
            try:
                self.pkg_dist_info = pkg_resources.get_distribution(pkg_name)
            except pkg_resources.DistributionNotFound:
                self.which = ''
            else:
                self.which = self.pkg_dist_info.location

    def is_available(self):
        """Return True if the tool is available, False otherwise."""
        return bool(self.which)

    def version(self):
        """Return the version string of the tool, or an empty string if the tool is not available."""
        return self.pkg_dist_info.version if self.which else ''


class ToolInfo:
    mock = [] # list of executable names to pretend missing. This is just fortesting purposes.

    def __init__(self, exe, accept_cluster_os_tools=False):
        """Check if tool 'exe' is available.

        :param str exe: name of an executable
        :param bool accept_cluster_os_tools: accept cluster operating system tools


        :return: SimpleNamespace(which,version), where which is the location of the tool or an empty
            string if it is not found or not accepted, and version is the version string (if requested)
            as returned be 'exe --version'.
        """
        self.exe = exe
        if exe in ToolInfo.mock:
            print(f'Mock: pretending tool `{exe}` is missing.')
            self.which = ''
        else:
            # completed_which = subprocess.run(['which', exe], capture_output=True, text=True)
            # self.which = completed_which.stdout.strip().replace('\n', ' ')
            self.which = shutil.which(exe)

        if self.which:
            if on_vsc_cluster() and not accept_cluster_os_tools and is_os_tool(self.which):
                self.which = ''

    def is_available(self):
        """Return True if the tool is available, False otherwise."""
        return bool(self.which)

    def version(self):
        """Return the version string of the tool, or an empty string if the tool is not available."""
        if self.which:
            completed_version = subprocess.run([self.exe, '--version'], capture_output=True, text=True)
            self.version = completed_version.stdout.strip().replace('\n\n','\n')#.replace('\n','\n        ')
        else:
            self.version = ''
        return self.version


def verify_project_name(project_name):
    """Project names must start with a char, and contain only chars, digits, underscores and dashes.

    :returns: bool
    """
    p = re.compile(r"\A[a-zA-Z][a-zA-Z0-9_-]*\Z")
    return bool(p.match(project_name))
