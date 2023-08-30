
from versioncontext import *
from versioncontext import _localversioncontext
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
        assert len(_localversioncontext.stack) == 1
    test()

@versioncontext((Test.foo, "2"))
def test_override_default_version():
    gvr = globalversionregistry
    lvc = _localversioncontext
    assert Test().foo() == 2

def test_context():
    assert len(_localversioncontext.stack) == 0

    with versioncontext(Test.foo):
        assert len(_localversioncontext.stack) == 1
        assert Test().foo() == 0

    assert len(_localversioncontext.stack) == 0

