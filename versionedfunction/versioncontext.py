import threading
from contextlib import ContextDecorator

from versionedfunction import *


class VersionContext:
    def __init__(self):
        self.map = {}

    def add(self, arg):
        if isinstance(arg, (list, tuple)) and len(arg) == 2:
            # (key, version)
            key, version = arg
            self.addKeyVersion(key, version)

    def addKeyVersion(self, key, version):
        versionInfo = None

        if isinstance(key, str):
            versionInfo = globalversionregistry.registryLookup(key)
        elif hasattr(key, 'versionInfo'):
            versionInfo = key.versionInfo


        if not versionInfo:
            raise Exception(f'Not Found in Version Registry: {key}')

        if not versionInfo.hasVersion(version):
            raise Exception(f'Found {key}, but no version {version}')

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

    def search(self, key):
        # search stack last first for key
        for vc in reversed(self.stack):
            found = vc.lookup(key)
            if found:
                return found

_localversioncontext = LocalVersionContext()

class versioncontext(ContextDecorator):
    def __init__(self, *args, **kwargs):
        self.args = args

    def __enter__(self):
        _localversioncontext.push()
        for arg in self.args:
            _localversioncontext.top().add(arg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        _localversioncontext.pop()
