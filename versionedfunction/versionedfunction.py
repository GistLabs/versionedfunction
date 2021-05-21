# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""


A bit of naming: vfunc is a versionedfunction, and vfuncv is a version of a versionedfunction
"""


def versionedfunction(vfunc):
    versionInfo = VersionInfo(vfunc)

    def version(vfuncv):
        versionInfo.addVersion(vfuncv)
        return vfuncv

    def default(vfuncv):
        versionInfo.setDefault(vfuncv)
        return vfuncv

    def vfunc_wrapper(*args, **kwargs):
        v = versionContext.lookupVersion(versionInfo.name)
        vfuncv = versionInfo.lookupFunction(v)
        return vfuncv(*args, **kwargs)

    vfunc_wrapper.versionInfo = versionInfo
    vfunc_wrapper.version = version
    vfunc_wrapper.default = default
    versionContext.register(versionInfo)

    return vfunc_wrapper

class VersionInfo():
    """
    This is used for each versionedfunction and connects the initial func and each version together
    """
    def __init__(self, vfunc):
        self.vfunc = vfunc
        self.versions = {}
        self.defaultVersion = None

    @property
    def name(self):
        return functionNameFrom(self.vfunc)

    def lookupFunction(self, v:str):
        if v: # some version is specified
            if v in self.versions:
                return self.versions[v]
            else:
                raise NameError(f'Version {v} not defined')
        else:
            if self.defaultVersion:
                return self.versions[self.defaultVersion]
            else:
                return self.vfunc

    def addVersion(self, vfuncv):
        versionName = versionFrom(self.vfunc.__name__, vfuncv.__name__)
        self[versionName] = vfuncv
        vfuncv.versionInfo = self

    def setDefault(self, vfuncv):
        self.defaultVersion = self.versionName(vfuncv)

    def __setitem__(self, key, value):
        self.versions[key] = value

    def versionName(self, vfuncv):
        return versionFrom(self.vfunc.__name__, vfuncv.__name__)

class VersionContext():
    """
    Global context to hold mapping from name to function to which version to use
    """
    def __init__(self):
        self.name2version = {}
        self.name2versionInfo = {} # populated during import/decorators

    def register(self, versionInfo):
        if versionInfo.name in self.name2versionInfo:
            raise NameError(f"Already registered function {versionInfo.name} in {self.name2versionInfo[versionInfo.name]}")
        self.name2versionInfo[versionInfo.name] = versionInfo

    def __getitem__(self, name):
        return self.name2version[name]

    def lookupVersion(self, name):
        if name in self.name2version:
            return self.name2version[name]
        else:
            return None

    def __setitem__(self, name, version):
        self.name2version[name] = version

versionContext = VersionContext() # versions to use for versionedfunctions, global context

def versionFrom(vfuncName, vfuncvName):
    """
    Remove the base versionedfunction name and left strip _ characters

    :param vfuncName: A versionedfunction name (string)
    :param vfuncvName: A function that is a version of a versionedfunction (name, string again)
    :return:
    """
    assert vfuncvName.startswith(vfuncName)
    return vfuncvName[len(vfuncName):].lstrip('_')

def functionNameFrom(vfunc):
    """
    The string used to identify a versionedfunction is defined by:
    * is the last two components of vfunc.__qualname__ [via split('.')]
    * if only 1 component, the prefix by module name of defining module

    class Foo():
        @versionedfunction
        def bar(self):
            pass
    would have 'Foo.bar" as __qualname__ and be used here to identify and map to versions

    <module_foo.py>
    @versionedfunction
    def bar():
        pass
    would have 'module_foo.bar' as name used to identify and map to versions

    This is intended to be a reasonable blend between fully qualified pathnames and only function name.
    """
    components = vfunc.__qualname__.split('.')[-2:] # last two components of name

    if len(components)<2:
        module = vfunc.__module__.split('.')[-1] # last module name
        components.insert(0, module)

    return '.'.join(components)