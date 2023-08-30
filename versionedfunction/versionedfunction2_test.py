# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""

"""

from versionedfunction2 import versionedfunction, versioncontext, globalversionregistry, localversioncontext
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

@versioncontext(Test.foo2)
def test_context_2():
    assert t.foo() == 2

@versioncontext(Test.foo)
def test_context_original():
    assert t.foo() == 0

def test_with_with():
    assert t.foo() == 1

    with versioncontext(Test.foo1):
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
    with versioncontext(A.x, B.y1):
        assert a.x() == 0 and b.y() == 1
    assert a.x() == 1 and b.y() == 2

    lvc = localversioncontext

    with versioncontext(A.x):
        assert a.x() == 0 and b.y() == 2

        with versioncontext(B.y1):
            assert a.x() == 0 and b.y() == 1

        assert a.x() == 0 and b.y() == 2

    assert a.x() == 1 and b.y() == 2

def test_version_then_default():
    class C:
        @versionedfunction
        def y(self):
            return 0

        @y.version
        def y1(self):
            return 1

        #@y.version
        @y.default
        def y2(self):
            return 2