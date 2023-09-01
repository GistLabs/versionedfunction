# Copyright (c) 2021-2023 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

import functools
import threading
from contextlib import ContextDecorator
from functools import cached_property


class VersionedException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GlobalVersionRegistry():
    """
    Global registry to hold mapping from key to versionedfunctions
    """
    def __init__(self):
        self._maps2vfunc = {}

    def _register(self, vfunc):
        if vfunc.key in self._maps2vfunc:
            raise NameError(f"Already registered function {vfunc.key}!")

        # map all the things that could be used to look up a VersionedFunction
        self._maps2vfunc[vfunc.key] = vfunc
        self._maps2vfunc[vfunc.func] = vfunc
        self._maps2vfunc[vfunc.wrapper] = vfunc

    def lookup(self, index):
        if index in self._maps2vfunc:
            return self._maps2vfunc[index]
        else:
            return None
globalversionregistry = GlobalVersionRegistry()

class VersionedFunction():
    """
    The data and structure around a function to be versioned

    @versionedfunction
    def foo():
        pass
    """
    def __init__(self, func, origin=None):
        self.func = func # the underlying function
        self._wrapper = None # the decorated and wrapper function

        self._default = None
        if not origin:
            self._default = self

        # either origin or versions but not both
        if not origin:
            origin = self
        self.origin = origin # the VersionedFunction for @versionedfunction decorated orignal version
        self.versions = [] # any versions of function

    @property
    def wrapper(self):
        return self._wrapper

    @wrapper.setter
    def wrapper(self, wrapper):
        if self._wrapper is not None:
            raise Exception()
        self._wrapper = wrapper

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, default):
        if self._default is not self:
            #already been changed
            raise VersionedException(f"{self.key} default version can't be changed to {default.key} because already {self._default.key}")
        self._default = default

    @cached_property
    def key(self):
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
        components = self.func.__qualname__.split('.')[-2:]  # last two components of name

        if len(components) < 2:
            module = self.func.__module__.split('.')[-1]  # last module name
            components.insert(0, module)

        return '.'.join(components)

    def register(self, funcv, vfuncv):
        self.versions.append(vfuncv)


def versionedfunction(func):
    vfunc = VersionedFunction(func)

    def version(funcv):
        if hasattr(funcv, 'vfunc'):
            # already created, just return wrapped func
            vfuncv = funcv.vfunc
            return vfuncv.wrapper

        vfuncv = VersionedFunction(funcv, vfunc)

        def funcv_wrapper(*args, **kwargs):
            # todo add warning or error if called directly here
            return funcv(*args, **kwargs)

        vfuncv.wrapper = funcv_wrapper
        funcv_wrapper.vfunc = vfuncv

        globalversionregistry._register(vfuncv)

        functools.update_wrapper(funcv_wrapper, funcv)
        return funcv_wrapper

    def default(funcv):
        funcv_wrapper = version(funcv)
        vfuncv = funcv_wrapper.vfunc

        vfunc.default = vfuncv

        return funcv_wrapper

    def func_wrapper(*args, **kwargs):
        vfuncv = localversioncontext.searchForVersion(vfunc)
        if not vfuncv:
            vfuncv = vfunc.default
        return vfuncv.func(*args, **kwargs)

    vfunc.wrapper = func_wrapper

    func_wrapper.version = version
    func_wrapper.default = default
    func_wrapper.vfunc = vfunc

    globalversionregistry._register(vfunc)

    functools.update_wrapper(func_wrapper, func)
    return func_wrapper


class VersionContext:
    def __init__(self):
        self.orig2version = {}

    def add(self, args):
        for arg in args:
            vfunc = globalversionregistry.lookup(arg)

            if not vfunc:
                raise VersionedException(f'{arg} is not a registered versionedfunction')
            else:
                origin = vfunc.origin

                if origin in self.orig2version and vfunc != self.orig2version[origin]:
                    raise NameError(f'{vfunc.key} already registered with version {self.orig2version[origin].key}')

                self.orig2version[origin] = vfunc

    def lookup(self, key):
        if key in self.orig2version:
            return self.orig2version[key]
        else:
            return None

class LocalVersionContext(threading.local):
    stack = []

    def push(self):
        # todo copy dict from previous to next, that way all values present and can check consistenty
        self.stack.append(VersionContext())

    def pop(self):
        self.stack.pop(-1)

    def top(self) -> VersionContext:
        return self.stack[-1]

    def searchForVersion(self, key):
        # search stack last first for key
        for vc in reversed(self.stack):
            found = vc.lookup(key)
            if found:
                return found

localversioncontext = LocalVersionContext()

class versionedcontext(ContextDecorator):
    def __init__(self, *args, **kwargs):
        self.args = args

    def __enter__(self):
        localversioncontext.push()
        localversioncontext.top().add(self.args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        localversioncontext.pop()
