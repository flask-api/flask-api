# Renderers

Renderers are responsible for taking the response value from your view and transforming it into a string or bytestring that will be used as the response body.

Flask API includes a few built-in renderer classes and also provides support for defining your own custom renderers.

## Determining the renderer

The set of valid renderers for a view is always defined as a list of classes.  When a view is entered Flask API will perform content negotiation on the incoming request, and determine the most appropriate renderer to satisfy the request.

The basic process of content negotiation involves examining the request's `Accept` header, to determine which media types it expects in the response.

## Setting the renderers

The default set of renderers may be set globally, using the `DEFAULT_RENDERERS` configuration key.  The default configuration will render to JSON as standard, or will render the browsable API if the client requests HTML.

    app.config['DEFAULT_RENDERERS'] = [
        'flask.ext.api.renderers.JSONRenderer',
        'flask.ext.api.renderers.BrowsableAPIRenderer',
    ]

You can also set the renderers used for an individual view, using the `set_renderers` decorator.

    from flask.ext.api.decorators import set_renderers
    from flask.ext.api.renderers import JSONRenderer

    ...

    @app.route('/example_view/')
    @set_renderers(JSONRenderer, MyCustomXMLRenderer)
    def example():
        return {'example': 'Setting renderers on a per-view basis'}

## Ordering of renderers

It's important when specifying the renderer classes for your API to think about what priority you want to assign to each media type.  If a client underspecifies the representations it can accept, such as sending an `Accept: */*` header, or not including an `Accept` header at all, then Flask API will select the first renderer in the list to use for the response.

---

# API Reference

## JSONRenderer

Renders the request data into `JSON`.

The client may additionally include an `'indent'` media type parameter, in which case the returned `JSON` will be indented.  For example `Accept: application/json; indent=4`.

    {
        "example": "indented JSON"
    }

**`media_type`**: `application/json`

**`charset`**: `None`

## HTMLRenderer

A simple renderer that simply returns pre-rendered HTML.  Unlike other renderers, the data passed to the response object should be a string representing the content to be returned.

An example of a view that uses `HTMLRenderer`:

    @app.route('/hello-world/')
    @set_renderers(HTMLRenderer)
    def hello_world(): 
        return '<html><body><h1>Hello, world</h1></body></html>'

You can use `HTMLRenderer` either to return regular HTML pages using Flask API, or to return both HTML and API responses from a single endpoint.

**`media_type`**: `text/html`

**`charset`**: `utf-8`

## BrowsableAPIRenderer

Renders data into HTML for the Browsable API.  This renderer will determine which other renderer would have been given highest priority, and use that to display an API style response within the HTML page.

**`media_type`**: `text/html`

**`charset`**: `utf-8`

---

# Custom renderers

To implement a custom renderer, you should override `BaseRenderer`, set the `.media_type`  property, and implement the `.render(self, data, media_type, **options)` method.

The method should return a string or bytestring, which will be used as the body of the HTTP response.

The arguments passed to the `.render()` method are:

**`data`**

The request data, returned by the view.

**`media_type`**

Optional.  If provided, this is the accepted media type, as determined by the content negotiation stage.

Depending on the client's `Accept:` header, this may be more specific than the renderer's `media_type` attribute, and may include media type parameters.  For example `"application/json; api-version="0.1"`.

**`**options`**

Any additional contextual arguments that may be required in order to render the response.
By default this includes:

* `status` - A string representing the response status.
* `status_code` - An integer representing the response status code.
* `headers` - A dictionary containing the response headers.

## Example

The following is an custom renderer that returns YAML.

    from flask.ext.api import renderers
    import yaml


    class YAMLRenderer(renderers.BaseRenderer):
        media_type = 'application/yaml'
        
        def render(self, data, media_type, **options):
            return yaml.dump(data, encoding=self.charset)

<!--
TODO: This needs testing, and probably some more work.

## Setting the character set

By default renderer classes are assumed to be using the `UTF-8` encoding.  To use a different encoding, set the `charset` attribute on the renderer.

    class PlainTextRenderer(renderers.BaseRenderer):
        media_type = 'text/plain'
        charset = 'iso-8859-1'

        def render(self, data, media_type, **options):
            return data.encode(self.charset)

Note that if a renderer class returns a unicode string, then the response content will be coerced into a bytestring, with the `charset` attribute set on the renderer used to determine the encoding.

If the renderer returns a bytestring representing raw binary content, you should set a charset value of `None`, which will ensure the `Content-Type` header of the response will not have a `charset` value set.
-->

[browser-accept-headers]: http://www.gethifi.com/blog/browser-rest-http-accept-headers
[rfc4627]: http://www.ietf.org/rfc/rfc4627.txt
