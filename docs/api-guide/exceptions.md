# Exceptions

When dealing with errors in Flask API you should typically raise one of the built-in exceptions, or a subclass of the base `APIException`.  Exceptions raised in this way will get the standard content negotiation applied to the response and will be rendered with an appropriate renderer.

By default all error responses will include a key `detail` in the body of the response.

For example, the following request:

    POST http://api.example.com/foo/bar HTTP/1.1
    Content-Type: application/json
    Content-Length: 63
    
    {'malformed json': 'keys and values should use double quotes'}

Might receive an error response indicating that the JSON content of the request is malformed:

    HTTP/1.1 400 Bad Request
    Content-Type: application/json
    Content-Length: 33

    {"detail": "Malformed request."}

---

## APIException

**Signature:** `APIException()`

The **base class** for all exceptions raised inside Flask API.

To provide a custom exception, subclass `APIException` and set the `.status_code` and `.detail` properties on the class.

For example, if your API relies on a third party service that may sometimes be unreachable, you might want to implement an exception for the "503 Service Unavailable" HTTP response code.  You could do this like so:

    from flask.ext.api.exceptions import APIException

    class ServiceUnavailable(APIException):
        status_code = 503
        detail = 'Service temporarily unavailable, try again later.'

## ParseError

**Signature:** `ParseError(detail=None)`

Raised if the request contains malformed data when accessing `request.data`, `request.form` or `request.files`.

By default this exception results in a response with the HTTP status code "400 Bad Request".

## AuthenticationFailed

**Signature:** `AuthenticationFailed(detail=None)`

Should be raised when an incoming request includes incorrect authentication.

By default this exception results in a response with the HTTP status code "401 Unauthenticated".

## NotAuthenticated

**Signature:** `NotAuthenticated(detail=None)`

Should be raised when an unauthenticated request fails permission checks.

By default this exception results in a response with the HTTP status code "401 Unauthenticated".

## PermissionDenied

**Signature:** `PermissionDenied(detail=None)`

Should be raised when an authenticated request fails permission checks.

By default this exception results in a response with the HTTP status code "403 Forbidden".

## NotFound

**Signature:** `NotFound(detail=None)`

Should be raised when a request is made to a resource that does not exist.

By default this exception results in a response with the HTTP status code "404 Not Found".

<!-- Currently 405's will result in Flask's default behavior.
## MethodNotAllowed

**Signature:** `MethodNotAllowed(method, detail=None)`

Raised when an incoming request occurs that does not map to a handler method on the view.

By default this exception results in a response with the HTTP status code "405 Method Not Allowed".
-->

## NotAcceptable

**Signature:** `NotAcceptable(detail=None)`

Raised if there are no renderers that can satisfy the client's requested `Accept` header.

By default this exception results in a response with the HTTP status code "406 Not Acceptable".

## UnsupportedMediaType

**Signature:** `UnsupportedMediaType(detail=None)`

Raised if there are no parsers that can handle the content type of the request data when accessing `request.data`, `request.form` or `request.files`.

By default this exception results in a response with the HTTP status code "415 Unsupported Media Type".

## Throttled

**Signature:** `Throttled(detail=None)`

Should be raised when an incoming request fails throttling checks.

By default this exception results in a response with the HTTP status code "429 Too Many Requests".

[cite]: http://www.doughellmann.com/articles/how-tos/python-exception-handling/index.html
[authentication]: authentication.md
