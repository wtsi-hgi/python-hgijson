# Change Log
## 3.1.0 - 2018-01-23
### Added
- Support for working with nested JSON properties.

## 3.0.1 - 2018-01-17
### Removed
- Unused imports. 


## 3.0.0 - 2018-01-16
## Added
- Ability to use custom collections with the `collection_factory` and `collection_iter` parameters.

### Changed
- Refactored tests.
- Renamed subpackage from `types` -> `custom_types` to avoid namespace clash with standard library. 

### Removed
- Test dependency on legacy `hgicommon` library.
- `SetJSONDecoder` and `SetJSONEncoder` (use `collection_factory=set` instead).


## 2.0.0 - 2018-01-08
### Changed
- Renamed subpackage from `json` -> `json_converters` to avoid namespace clash with standard library.
- Moved from using `nose` -> `unittest` for testing.
- Only the first 3 arguments of `JsonPropertyMapping` can be used as args: the remainder must be kwargs.

### Removed
- Ability to pass arguments through arbitrary arguments from `JsonPropertyMapping` to `PropertyMapping`
- Use of args with `PropertyMapping` (kwargs only).


## 1.5.0 - 2017-11-16 
### Changed
- Moved to using a PyPi version of 
[HGI's common Python library](https://github.com/wtsi-hgi/python-common) for 
testing, opposed to using it from GitHub.
- Fixed bug in `DatetimeISOFormatJSONDecoder`.


## 1.4.3 - 2016-08-30
### Added
- Support for defining encoders/decoders for objects with properties of the same type 
([#19](https://github.com/wtsi-hgi/python-json/issues/19)).

### Changed
- Moved the documentation over to ReadTheDocs, opposed to bundling it all in the README.


## 1.4.2 - 2016-08-04
### Changed
- Fix for issue with fix in `1.4.1`.


## 1.4.1 - 2016-08-04
### Changed
- Fixed bug in serialisation of `None`, 
[reported](https://github.com/wtsi-hgi/python-json/issues/16#issuecomment-237527405) by 
[YuriIvanov](https://github.com/YuriIvanov) ([#18](https://github.com/wtsi-hgi/python-json/issues/18)).


## 1.4.0 - 2016-08-04
### Changed
- Encoders now serialise `None` to `null` and visa-versa for decoders (thanks to 
[YuriIvanov](https://github.com/YuriIvanov) for bringing this improvement to light in 
[#16](https://github.com/wtsi-hgi/python-json/issues/16)) ([#17](https://github.com/wtsi-hgi/python-json/issues/17)).
- Corrected self-referential type hinting. 


## 1.3.1 - 2016-05-19
### Changed
- Corrections to `setup.py`.


## 1.3.0 - 2016-05-19
### Added
- Documentation on how to serialize to/from a dictionary opposed to a string.
- Documentation on how to install the library, import methods/classes and develop.
- imports via `__init__.py`.

### Changed
- Removed useless equality and hash calculation methods on `PropertyMapping`.
- Improvements to documentation.

### Removed
- Helper test runner scripts.


## 1.2.2 - 2016-05-18
### Changed
- Hotfix for dependency installation when installed via PyPI.


## 1.2.1 - 2016-05-18
### Changed
- Hotfix for package installation via PyPI.


## 1.2.0 - 2016-05-18
### Added
- Added documentation on how the order of mappings is determined when using mappers and inheritance.

### Changed
- Sorted packing to allow upload as package to PyPI.
- Changed license from GPL to MIT.

### Removed
- Dependency on `hgicommon` library (still required for testing though).

## 1.0.0 - 2016-04-14
- First stable release.
