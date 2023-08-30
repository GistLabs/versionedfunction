
from versionedfunction import *


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
        assert len(localversioncontext.stack) == 1
    test()

@versioncontext((Test.foo, "2"))
def test_override_default_version():
    gvr = globalversionregistry
    lvc = localversioncontext

    r = Test().foo()
    assert lvc.searchForVersion('Test.foo') == '2'
    assert r == 2

def test_context():
    assert len(localversioncontext.stack) == 0

    with versioncontext(Test.foo):
        assert len(localversioncontext.stack) == 1
        assert Test().foo() == 0

    assert len(localversioncontext.stack) == 0

