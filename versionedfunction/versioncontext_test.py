
from versioncontext import *
from versioncontext import _globalversionregistry, _localversioncontext
from versionedfunction import versionedfunction


class Test():
    @versionedfunction
    def foo(self):
        return 0

    @foo.version
    @foo.default
    def foo1(self):
        return 1

    @foo.version
    def foo2(self):
        return 2


def test_decorator():
    @versioncontext(Test.foo2)
    def test():
        assert len(_localversioncontext.stack) == 2
    test()

@versioncontext(Test.foo, "str")
def test_default_version():
    assert 1==1

def test_context():
    assert len(_localversioncontext.stack) == 1

    with versioncontext2(Test.foo) as vc:
        assert len(_localversioncontext.stack) == 2

    assert len(_localversioncontext.stack) == 1

