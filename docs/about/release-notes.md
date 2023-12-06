# Release Notes

## Version 3.2

- Fixed support for Flask `3.0`

## Version 3.1

- Fixed support for Flask `2.3`.

## Version 3.0

* Dropped support for Flask `<2.0`.

## Version 2.0

* Dropped support for Python `<3.6`.
* Dropped support for Flask `<1.1`.

## Version 1.1

* Added support for custom JSON encoders.
* Added `None` as a valid return value for empty responses (204).
* Dropped support for Flask `<0.12.3` due to [CVE-2018-1000656](https://nvd.nist.gov/vuln/detail/CVE-2018-1000656).
* Added support for `python-markdown` 3+.

## Version 1.0

* Stable release to enter maintenance mode.

## Version 0.7.1

* Added customization of automatic API return types (`app.response_class.api_return_types`).

## Version 0.7

* Disabled rendering of text responses as API views.
* Added additional HTTP status codes.

## Version 0.6.9

* Fixed `AttributeError` when rendering empty content using `BrowsableAPIRenderer`

## Version 0.6.8

* Fixed `AttributeError` with Blueprint handlers in Flask 0.11+

## Version 0.6.7

* Fixed compatibility issue between Flask 0.10 and 0.11

## Version 0.6.6

* Updated dependencies to allow newer versions of Flask

## Version 0.6.5

* Replaced periods in page titles with spaces

## Version 0.6.4

* Fixed escaping in link headers
* Added support for Markdown in the browsable API (requires `markdown >= 2.1`)

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
