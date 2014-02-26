# Parsers

Parsers are responsible for taking the content of the request body as a bytestream, and transforming it into a native Python data representation.

Flask API includes a few built-in parser classes and also provides support for defining your own custom parsers.

## How the parser is determined

The set of valid parsers for a view is always defined as a list of classes.  When any of the properties `request.data`, `request.form` or `request.files` are accessed, Flask API will examine the `Content-Type` header on the incoming request, and determine which parser to use to handle the request content.

---

**Note**: When developing client applications always remember to make sure you're setting the `Content-Type` header when sending data in an HTTP request.

If you don't set the content type, most clients will default to using `'application/x-www-form-urlencoded'`, which may not be what you wanted.

As an example, if you are sending `json` encoded data using jQuery with the [.ajax() method][jquery-ajax], you should make sure to include the `contentType: 'application/json'` setting.

---

## Setting the parsers

The default set of parsers may be set globally, using the `DEFAULT_PARSERS` configuration key.  The default configuration will deal with parsing either JSON or form encoded requests.

    app.config['DEFAULT_PARSERS'] = [
        'flask.ext.api.parsers.JSONParser',
        'flask.ext.api.parsers.URLEncodedParser',
        'flask.ext.api.parsers.MultiPartParser'
    ]

You can also set the parsers used for an individual view, using the `set_parsers` decorator.

    from flask.ext.api.decorators import set_parsers
    from flask.ext.api.parsers import JSONParser

    ...

    @app.route('/example_view/')
    @set_parsers(JSONParser, MyCustomXMLParser)
    def example():
        return {
            'example': 'Setting renderers on a per-view basis',
            'request data': request.data
        }

---

# API Reference

## JSONParser

Parses `JSON` request content and populates `request.data`.

**media_type**: `application/json`

## FormParser

Parses HTML form content.  `request.data` will be populated with a `MultiDict` of data.

You will typically want to use both `FormParser` and `MultiPartParser` together in order to fully support HTML form data.

**media_type**: `application/x-www-form-urlencoded`

## MultiPartParser

Parses multipart HTML form content, which supports file uploads.  Both `request.data` and `request.files` will be populated with a `MultiDict`.

You will typically want to use both `FormParser` and `MultiPartParser` together in order to fully support HTML form data.

**media_type**: `multipart/form-data`

---

# Custom parsers

To implement a custom parser, you should override `BaseParser`, set the `.media_type` property, and implement the `.parse(self, stream, media_type, **options)` method.

The method should return the data that will be used to populate the `request.data` property.

The arguments passed to `.parse()` are:

**`stream`**

A bytestream representing the body of the request.

**`media_type`**

An instance of MediaType indicating media type of the incoming request.

Depending on the request's `Content-Type:` header, this may be more specific than the renderer's `media_type` attribute, and may include media type parameters.  For example `"text/plain; charset=utf-8"`.

**`**options`**

Any additional contextual arguments that may be required in order to parse the request.
By default this includes a single keyword argument:

* `content_length` - An integer representing the length of the request body in bytes.

## Example

The following is an example plaintext parser that will populate the `request.data` property with a string representing the body of the request. 

    class PlainTextParser(BaseParser):
        """
        Plain text parser.
        """
        media_type = 'text/plain'

        def parse(self, stream, media_type, **options):
            """
            Simply return a string representing the body of the request.
            """
            return stream.read().decode('utf8')

[jquery-ajax]: http://api.jquery.com/jQuery.ajax/
