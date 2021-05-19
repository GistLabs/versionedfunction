# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""

"""

from versionedfunction import versionedfunction, versionContext, versionFrom
import pytest

@versionedfunction
def fooAlgo():
    return 0

def test_decorator():
    assert fooAlgo() == 0

@fooAlgo.version
def fooAlgo_v1():
    return 1

def test_fooAlgo_version_annotation():
    return fooAlgo_v1 == 1

def test_fooAlgo_versionInfo():
    assert fooAlgo.versionInfo.name == 'versionedfunction_test.fooAlgo'

def test_fooAlgo_v1_in_versions():
    assert fooAlgo.versionInfo is not None
    assert fooAlgo.versionInfo['v1'] == fooAlgo_v1

@fooAlgo.version
def fooAlgo_v2():
    return 2

def test_fooAlgo_v2_in_versions():
    assert fooAlgo.versionInfo['v2'] == fooAlgo_v2

def test_call_v2():
    versionContext['versionedfunction_test.fooAlgo'] = 'v2'
    assert fooAlgo() == 2

@versionedfunction
def barAlgo(a, b):
    return barAlgoV1(a, b)

@barAlgo.version
def barAlgoV1(a, b):
    return a + b + 1

def test_barAlgo():
    assert barAlgoV1(1, 2) == 4
    assert barAlgo(1, 2) == 4

@barAlgo.version
def barAlgoV2(a, b):
    return a + b + 2

def test_change_version():
    versionContext['versionedfunction_test.barAlgo'] = None
    assert barAlgo(1, 1) == 3
    versionContext['versionedfunction_test.barAlgo'] = 'V1'
    assert barAlgo(1, 1) == 3 # same as before
    versionContext['versionedfunction_test.barAlgo'] = 'V2'
    assert barAlgo(1, 1) == 4 # now use other version
    versionContext['versionedfunction_test.barAlgo'] = None
    assert barAlgo(1, 1) == 3 # back to default

def test_bad_version_fails():
    versionContext['versionedfunction_test.barAlgo'] = None # None is ok
    assert barAlgo(1, 1) == 3
    versionContext['versionedfunction_test.barAlgo'] = '' # Empty string is ok
    assert barAlgo(1, 1) == 3
    with pytest.raises(NameError, match="Version xyz not defined"):
        versionContext['versionedfunction_test.barAlgo'] = 'xyz'  # NOT ok
        assert barAlgo(1, 1) == 3

def test_registered_names():
    assert versionContext.name2versionInfo['versionedfunction_test.barAlgo'] == barAlgo.versionInfo
    assert versionContext.name2versionInfo['versionedfunction_test.fooAlgo'] == fooAlgo.versionInfo

def test_not_double_register():
    with pytest.raises(NameError, match="Already registered function versionedfunction_test.barAlgo"):
        class versionedfunction_test():
            @versionedfunction
            def barAlgo(self):
                pass
        assert versionedfunction_test.barAlgo.versionInfo.name == "versionedfunction_test.barAlgo"

def test_func2name():
    assert versionedfunction.__module__ == "versionedfunction.versionedfunction"
    assert versionedfunction.__qualname__ == 'versionedfunction'
    assert versionFrom.__qualname__ == 'versionFrom'

def test_method2name():
    assert versionContext.register.__qualname__ == 'VersionContext.register'
    assert versionContext.register.__module__ == "versionedfunction.versionedfunction"

def test_nestedModuleName():
    assert 'email.mime.text'.split('.')[-1] == 'text'
    assert 'text'.split('.')[-1] == 'text'

def test_listSlice():
    x = (1, 2, 3)
    assert x[-2:] == (2, 3)

    y = (3,)
    assert y[-2:] == (3,)
