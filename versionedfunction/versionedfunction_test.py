# Copyright (c) 2021 John Heintz, Gist Labs https://gistlabs.com
# License Apache v2 http://www.apache.org/licenses/

"""

"""

from versionedfunction import versionedfunction


@versionedfunction
def fooAlgo():
    return 1

def test_decorator():
    assert fooAlgo() == 1
