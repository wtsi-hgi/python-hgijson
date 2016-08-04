# Change Log
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
