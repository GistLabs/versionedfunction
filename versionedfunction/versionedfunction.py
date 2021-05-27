# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""


Naming is hard:
 * vfunc is a versionedfunction, and vfuncv is a version of a versionedfunction
 * versionKey is unique string to identify versionedfunction, like 'Foo.algo' or 'modulename.vfunc'
 * versionName is the version designation, like 2 or v3 or version4
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
        versionName = versionContext.lookupVersion(versionInfo.key)
        vfuncv = versionInfo.lookupFunction(versionName)
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
        self.defaultVersionName = None

    @property
    def key(self):
        return functionKeyFrom(self.vfunc)

    def lookupFunction(self, versionName:str):
        if versionName: # some version is specified
            if versionName in self.versions:
                return self.versions[versionName]
            else:
                raise NameError(f'Version {versionName} not defined')
        else:
            if self.defaultVersionName:
                return self.versions[self.defaultVersionName]
            else:
                return self.vfunc

    def addVersion(self, vfuncv):
        versionName = versionNameFrom(self.vfunc.__name__, vfuncv.__name__)
        self[versionName] = vfuncv
        vfuncv.versionInfo = self

    def setDefault(self, vfuncv):
        self.defaultVersionName = self.versionName(vfuncv)

    def __setitem__(self, key, value): # TODO oh jeez these names are confusing here
        self.versions[key] = value

    def versionName(self, vfuncv):
        return versionNameFrom(self.vfunc.__name__, vfuncv.__name__)

class VersionContext():
    """
    Global context to hold mapping from key to which version to use for a versionedfunction
    """
    def __init__(self):
        self.key2version = {}
        self.key2versionInfo = {} # populated during import/decorators

    def register(self, versionInfo):
        if versionInfo.key in self.key2versionInfo:
            raise NameError(f"Already registered function {versionInfo.key} in {self.key2versionInfo[versionInfo.key]}")
        self.key2versionInfo[versionInfo.key] = versionInfo

    def __getitem__(self, key):
        return self.key2version[key]

    def lookupVersion(self, key):
        if key in self.key2version:
            return self.key2version[key]
        else:
            return None

    def __setitem__(self, key, version):
        self.key2version[key] = version

versionContext = VersionContext() # versions to use for versionedfunctions, global context

def versionNameFrom(vfunc_str, vfuncv_str):
    """
    Remove the base versionedfunction name and left strip _ characters

    :param vfunc_str: A versionedfunction name (string)
    :param vfuncv_str: A function that is a version of a versionedfunction (name, string again)
    :return:
    """
    assert vfuncv_str.startswith(vfunc_str)
    return vfuncv_str[len(vfunc_str):].lstrip('_')

def functionKeyFrom(vfunc):
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