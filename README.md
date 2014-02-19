# FlaskAPI

**Work in progress**

[![Build Status][travis-image]][travis-link]
[![Coverage Status][coveralls-image]][coveralls-link]

## Installation

Install using `pip`.

    pip install flaskapi

Import and initialize your application.

    from flaskapi import FlaskAPI

    app = FlaskAPI(__main__)

## Returning responses

Return any valid response object as normal, or return a `list` or `dict`.

    @app.route('/example/')
    def example():
        return {'hello': 'world'}

## Request data

Access the parsed request data using `request.data`.  This will handle JSON or form data by default.

    @app.route('/example/')
    def example():
        return {'request data': request.data}

[travis-image]: https://travis-ci.org/tomchristie/flaskapi.png?branch=master
[travis-link]: https://travis-ci.org/tomchristie/flaskapi
[coveralls-image]: https://coveralls.io/repos/tomchristie/flaskapi/badge.png?branch=master
[coveralls-link]: https://coveralls.io/r/tomchristie/flaskapi?branch=master
