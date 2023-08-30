import functools
import threading
from contextlib import ContextDecorator


class GlobalVersionRegistry:
    def __init__(self):
        self.key2versionInfo = {}

_globalversionregistry = GlobalVersionRegistry()


class VersionContext:
    pass


class LocalVersionContext(threading.local):
    stack = [VersionContext(),]

    def push(self):
        self.stack.append(VersionContext())

    def pop(self):
        self.stack.pop(0)

    def top(self) -> VersionContext:
        return self.stack[-1]

_localversioncontext = LocalVersionContext()

class versioncontext(ContextDecorator):
    def __init__(self, *context):
        self.context = context

    def __enter__(self):
        _localversioncontext.push()
        # resolve self.args to versionfunction refs

    def __exit__(self, exc_type, exc_val, exc_tb):
        _localversioncontext.pop()
