from __future__ import unicode_literals
from flaskapi import status


class APIException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ''

    def __init__(self, detail=None):
        if detail is not None:
            self.detail = detail

    def __str__(self):
        return self.detail


class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Malformed request.'


# class AuthenticationFailed(APIException):
#     status_code = status.HTTP_401_UNAUTHORIZED
#     default_detail = 'Incorrect authentication credentials.'


# class NotAuthenticated(APIException):
#     status_code = status.HTTP_401_UNAUTHORIZED
#     default_detail = 'Authentication credentials were not provided.'


# class PermissionDenied(APIException):
#     status_code = status.HTTP_403_FORBIDDEN
#     default_detail = 'You do not have permission to perform this action.'


# class MethodNotAllowed(APIException):
#     status_code = status.HTTP_405_METHOD_NOT_ALLOWED
#     default_detail = 'Request method "%s" not allowed.'

#     def __init__(self, method, detail=None):
#         self.detail = (detail or self.default_detail) % method


class NotAcceptable(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    detail = 'Could not satisfy the request Accept header.'


class UnsupportedMediaType(APIException):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    detail = 'Unsupported media type in the request Content-Type header.'


# class Throttled(APIException):
#     status_code = status.HTTP_429_TOO_MANY_REQUESTS
#     default_detail = 'Request was throttled.'
#     extra_detail = 'Expected available in %d second%s.'

#     def __init__(self, wait=None, detail=None):
#         if wait is None:
#             self.detail = detail or self.default_detail
#             self.wait = None
#         else:
#             format = (detail or self.default_detail) + ' ' + self.extra_detail
#             self.detail = format % (wait, wait != 1 and 's' or '')
#             self.wait = math.ceil(wait)
