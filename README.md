# versionedfunction
Sometimes you want to be able to dynamically call different 
versions of a function.
* testing alternatives against each other
* runtime "always on" support for versions code changes

## Example

```python
from versionedfunction import versionedfunction, versionedcontext


class Foo():
    @versionedfunction
    def algo(self):
        return 0

    @algo.version
    def algo1(self):
        return 1

    @algo.version
    @algo.default
    def algo2(self):
        return 2


foo = Foo()

# the default is algo2
assert foo.algo() == 2

with versionedcontext(Foo.algo):
    # choose Foo.algo
    assert foo.algo() == 0

@versionedcontext(Foo.algo1)
def some_method():
    assert foo.algo() == 1
```

## Installing
```bash
$ pip install versionedfunction
```
The source code is currently hosted on GitHub at 
https://github.com/GistLabs/versionedfunction
and published in PyPI at https://pypi.org/project/versionedfunction/ 

The versioning scheme currently used is {major}.{minor}.{auto build number}
from `git rev-list --count HEAD`. 

We recommend picking a version like:

`versionedfunction = "^0.9"`

## Community guidelines
We welcome contributions and questions. Please head over to github and 
send us pull requests or create issues!
