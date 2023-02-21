# versionedfunction
Sometimes you want to be able to dynamically call different 
versions of a function.
* testing alternatives against each other
* runtime "always on" support for versions code changes

## Example
```python
from versionedfunction import versionedfunction, versionContext

class Foo():
    @versionedfunction
    def algo(self):
        return 0

    @algo.version
    def algo1(self):
        return 1

    @algo.default
    @algo.version
    def algo2(self):
        return 2
foo = Foo()

assert foo.algo() == 2

versionContext['Foo.algo'] = "1"
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

`versionedfunction = "^0.8"`

## Community guidelines
We welcome contributions and questions. Please head over to github and 
send us pull requests or create issues!
