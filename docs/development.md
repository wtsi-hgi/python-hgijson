# Development
## Setup
Install both library dependencies and the dependencies needed for testing:
```bash
$ pip3 install -q -r requirements.txt
$ pip3 install -q -r test_requirements.txt
```

## Testing
Using nosetests, in the project directory, run:
```bash
$ nosetests -v
```

To generate a test coverage report with nosetests:
```bash
$ nosetests -v --with-coverage --cover-package=hgijson --cover-inclusive
```
