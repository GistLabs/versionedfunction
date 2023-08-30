# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

import threading
from contextlib import ContextDecorator

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
        vfuncv.versionInfo = versionInfo
        return vfuncv

    def default(vfuncv):
        versionInfo.setDefault(vfuncv)
        return vfuncv

    def vfunc_wrapper(*args, **kwargs):
        versionName = globalversionregistry.lookupVersion(versionInfo.key)
        vfuncv = versionInfo.lookupFunction(versionName)
        return vfuncv(*args, **kwargs)

    vfunc_wrapper.versionInfo = versionInfo
    vfunc_wrapper.original = vfunc
    vfunc_wrapper.version = version
    vfunc_wrapper.default = default
    globalversionregistry.register(versionInfo)

    return vfunc_wrapper

class VersionInfo():
    """
    This is used for each versionedfunction and connects the initial func and each version together
    """
    def __init__(self, vfunc):
        self.vfunc = vfunc
        self.versions = {}
        self.versions[vfunc.__name__] = vfunc # special case to support original function
        self.defaultVersionName = None

    @property
    def key(self):
        return functionKeyFrom(self.vfunc)

    def hasVersion(self, versionName:str):
        return versionName in self.versions

    def findFuncForVersion(self, versionName:str):
        reversed = {v: k for k, v in self.versions.items()}
        if versionName in reversed:
            return reversed[versionName]
        else:
            return None

    def lookupFunction(self, versionName:str):
        if versionName: # some version is specified
            if versionName in self.versions:
                return self.versions[versionName]
            elif versionName == self.vfunc.__name__:
                return self.vfunc
            else:
                raise NameError(f'Version {versionName} not defined for {self.key}')
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

class GlobalVersionContext():
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

    def registryLookup(self, key) -> VersionInfo:
        if key in self.key2versionInfo:
            return self.key2versionInfo[key]
        else:
            return None

    def __getitem__(self, key):
        return self.key2version[key]

    def lookupVersion(self, key):
        version = localversioncontext.searchForVersion(key)
        if version: return version

        if key in self.key2version:
            return self.key2version[key]
        else:
            return None

    def __setitem__(self, key, version):
        self.key2version[key] = version

globalversionregistry = GlobalVersionContext() # versions to use for versionedfunctions, global context


class VersionContext:
    def __init__(self):
        self.map = {} # from str key to str version

    def add(self, args):
        """
        Support
            (key:str, version:str),
            ..., key, version:str, ...
            vfunc


        if arg(n) is vfunc, and arg(n+1) is str:
            key, version

        if arg(n) is vfunc(v) arg(n+1) is not str:
            vfunc(v) is used

        :param arg:
        :return:
        """
        for i in range(len(args)):
            arg = args[i]

            # tuple (key, version)
            if isinstance(arg, (list, tuple)) and len(arg) == 2:
                key, version = arg
                self.addKeyVersion(key, version)

            # lookahead and see if args[i+1] is version for args[i] vfunc
            #if i+1 <= len(args)-1 and isinstance(args(i+1), str):
            #    versionInfo = self.findVersionInfoFrom(args[i])
            #    version = args[i+1]

            # if vfuncv like Foo.algo4 reference
            if hasattr(args[i], 'versionInfo'):
                f = args[i]
                versionInfo = f.versionInfo
                if versionInfo.vfunc == f.original:
                    self.addKeyVersion(versionInfo.key, f.original.__name___)
                elif versionInfo.findFuncForVersion(f):
                    self.addKeyVersion(versionInfo.key, versionInfo.findFuncForVersion(f))
                else:
                    raise NameError(f'Found {versionInfo.key} but no version for {args[i]}')



    def addKeyVersion(self, key, version):
        versionInfo = self.findVersionInfoFrom(key)

        if not versionInfo.hasVersion(version):
            raise Exception(f'Found {key}, but no version {version}')

        self.map[versionInfo.key] = version

    def findVersionInfoFrom(self, key):
        versionInfo = None
        if isinstance(key, str):
            versionInfo = globalversionregistry.registryLookup(key)
        elif hasattr(key, 'versionInfo'):
            versionInfo = key.versionInfo
        if not versionInfo:
            raise Exception(f'Not Found in Version Registry: {key}')
        return versionInfo

    def lookup(self, key):
        if key in self.map:
            return self.map[key]
        else:
            return None


class LocalVersionContext(threading.local):
    stack = []

    def push(self):
        self.stack.append(VersionContext())

    def pop(self):
        self.stack.pop(0)

    def top(self) -> VersionContext:
        return self.stack[-1]

    def searchForVersion(self, key):
        # search stack last first for key
        for vc in reversed(self.stack):
            found = vc.lookup(key)
            if found:
                return found

localversioncontext = LocalVersionContext()

class versioncontext(ContextDecorator):
    def __init__(self, *args, **kwargs):
        self.args = args

    def __enter__(self):
        localversioncontext.push()
        localversioncontext.top().add(self.args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        localversioncontext.pop()



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