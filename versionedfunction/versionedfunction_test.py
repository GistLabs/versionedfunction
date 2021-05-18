# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""

"""

from versionedfunction import versionedfunction, versions



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

def test_fooAlgo_v1_in_versions():
    assert fooAlgo.versionInfo is not None
    assert fooAlgo.versionInfo['v1'] == fooAlgo_v1

@fooAlgo.version
def fooAlgo_v2():
    return 2

def test_fooAlgo_v2_in_versions():
    assert fooAlgo.versionInfo['v2'] == fooAlgo_v2

def test_call_v2():
    versions.clear()
    versions.append("v2")
    assert fooAlgo() == 2