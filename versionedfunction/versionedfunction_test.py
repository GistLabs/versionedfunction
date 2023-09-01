# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""

"""

from versionedfunction import versionedfunction, versionedcontext, VersionedException, VersionedFunction, localversioncontext
import pytest


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

t = Test()

def test_no_context_original():
    assert t.foo() == 1

@versionedcontext(Test.foo2)
def test_context_2():
    assert t.foo() == 2

@versionedcontext(Test.foo)
def test_context_original():
    assert t.foo() == 0

def test_with_with():
    assert t.foo() == 1

    with versionedcontext(Test.foo1):
        assert t.foo() == 1

    assert t.foo() == 1

def test_default():
    class D():
        @versionedfunction
        def a(self):
            return 0

        @a.default
        def a1(self):
            return 1

    d = D()

    assert d.a() == 1

def test_multiple_and_nested_contexts():
    class A:
        @versionedfunction
        def x(self):
            return 0

        @x.default
        @x.version
        def x1(self):
            return 1

    class B:
        @versionedfunction
        def y(self):
            return 0

        @y.version
        def y1(self):
            return 1

        @y.default
        def y2(self):
            return 2

    a = A()
    b = B()

    assert a.x() == 1 and b.y() == 2
    with versionedcontext(A.x, B.y1):
        assert a.x() == 0 and b.y() == 1
    assert a.x() == 1 and b.y() == 2

    lvc = localversioncontext

    with versionedcontext(A.x):
        assert a.x() == 0 and b.y() == 2

        with versionedcontext(B.y1):
            assert a.x() == 0 and b.y() == 1

        assert a.x() == 0 and b.y() == 2

    assert a.x() == 1 and b.y() == 2

def test_version_function_keys():
    VersionedFunction(Test.foo).key == 'Test.foo'
    VersionedFunction(Test.foo1).key == 'Test.foo1'

    VersionedFunction(test_default).key == f'versionedfunction2_test.{test_default.__name__}'


def test_not_versioned_fails():
    class E:
        def e(self):
            return 0

    with pytest.raises(VersionedException):
        with versionedcontext(E.e):
            pass


def test_version_then_default():
    class C:
        @versionedfunction
        def y(self):
            return 0

        @y.version
        def y1(self):
            return 1

        @y.version
        @y.default
        def y2(self):
            return 2

def test_version_repeat():
    class D:
        @versionedfunction
        def y(self):
            return 0

        @y.version
        @y.version
        def y1(self):
            return 1

def test_func_name_wrapped():
    assert Test.foo.__name__ == 'foo'
    assert Test.foo1.__name__ == 'foo1'
    assert Test.foo2.__name__ == 'foo2'
