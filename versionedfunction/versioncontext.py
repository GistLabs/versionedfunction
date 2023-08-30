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

class VersionContextDecorator(ContextDecorator):
    def __init__2(self, *args, **kwargs):
        print(f'__init__ {self} {args}')
        self.args = args
        self.kwargs = kwargs

    def __call__2(self, *args, **kwargs):
        print(f'__call__ {self} {args}')
        return VersionContextDecorator(args)

    def __enter__(self):
        _localversioncontext.push()
        # resolve self.args to versionfunction refs
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _localversioncontext.pop()

def versioncontext(*context):
    """
    Returns a function decorator, with access to args

    :param args: the versions to call
    :return:
    """

    if context is None and len(context) == 0:
        raise Exception("versioncontext must be called with some version information.")

    def inner_decorator(func=None, *args):

        def __enter__():
           _localversioncontext.push()
           # resolve self.args to versionfunction refs
           return None

        def __exit__(exc_type, exc_val, exc_tb):
            _localversioncontext.pop()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                _localversioncontext.push()
                return func(*args, **kwargs)
            finally:
                _localversioncontext.pop()

        #wrapper.__enter__ = __enter__
        #wrapper.__exit__ = __exit__

        return wrapper

    return inner_decorator


def versioncontext2(*context):
    """
    Returns a function decorator, with access to args

    :param args: the versions to call
    :return:
    """

    if context is None and len(context) == 0:
        raise Exception("versioncontext must be called with some version information.")

    def inner_decorator(func=None, *args):

        #@functools.wraps(func)
        class _context():
            def __call__(self, *args, **kwargs):
                try:
                    self.__enter__()
                    return func(*args, **kwargs)
                finally:
                    self.__exit__()

            def __enter__(self):
                _localversioncontext.push()

            def __exit__(self, exc_type, exc_val, exc_tb):
                _localversioncontext.pop()
        wrapper = _context()
        #wrapper = functools.wraps(wrapper)
        return wrapper

    return inner_decorator
