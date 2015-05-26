# Release Notes

This project is currently in alpha.  It is functional and well tested but you are advised to pay close attention to the release notes when upgrading to future versions.

## Version 0.6.3

* Fixed handling of query strings (in Python 3)
* Fixed handling of empty content in `APIResposne`
* Fixed escaping of angled brackets and ampersands
* Added support for custom templates when extending `BrowsableAPIRenderer`

## Version 0.6.2

* Added `HTMLRenderer`.

## Version 0.6.1

* `set_parsers` and `set_decorators` accept either positional args or a single arg list/tuple.
* Hyperlink content in the browsable API.

## Version 0.6

Initial alpha release.
