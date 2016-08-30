# Setup
## Installation
Stable releases can be installed via PyPI:
```bash
$ pip3 install hgijson
```

Bleeding edge versions can be installed directly from GitHub:
```bash
$ pip3 install git+https://github.com/wtsi-hgi/python-json.git@<commit_id_or_branch_or_tag>#egg=hgijson
```

To declare this library as a dependency of your project, add it to your `requirement.txt` file.


## Imports
All methods and classes can be imported with:
```python
from hgijson import *
```
Once what is required is known, 
[it is good practice](http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#importing) to import things 
explicitly, e.g.:
```python
from hgijson import JsonPropertyMapping, MappingJSONEncoderClassBuilder, MappingJSONDecoderClassBuilder
```
