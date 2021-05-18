# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""


A bit of naming: vfunc is a versionedfunction, and vfuncv is a version of a versionedfunction
"""

versions = [] # list of versions to use for versionedfunctions, global context

def versionedfunction(vfunc):
    versionInfo = VersionInfo(vfunc)# main data structure to hold state for versionedfunctions

    def version(vfuncv):
        """

        :param vfuncv: Functions to be versioned
        :return:
        """
        versionName = _find_version_name(vfunc.__name__, vfuncv.__name__)
        versionInfo[versionName] = vfuncv

        return vfuncv

    def vfunc_wrapper(*args, **kwargs):
        if versions:
            v = versions[0]
            f = versionInfo[v]
        else:
            f = vfunc
        return f(*args, **kwargs)

    vfunc_wrapper.versionInfo = versionInfo
    vfunc_wrapper.version = version

    return vfunc_wrapper

class VersionInfo():
    """
    This data structure is used for each versionedfunction and connects the initial and each version together
    """
    def __init__(self, vfunc):
        self.vfunc = vfunc
        self.versions = {}

    @property
    def name(self):
        return self.vfunc.__name__

    def __getitem__(self, item):
        return self.versions[item]

    def __setitem__(self, key, value):
        self.versions[key] = value

def _find_version_name(vfuncName, vfuncvName):
    """
    Remove the base versionedfunction name and left strip - characters

    :param vfuncName: A versionedfunction name (string)
    :param vfuncvName: A function that is a version of a versionedfunction (name, string again)
    :return:
    """
    assert vfuncvName.startswith(vfuncName)
    return vfuncvName[len(vfuncName):].lstrip('_')
