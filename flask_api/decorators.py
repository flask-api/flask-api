from functools import wraps
from flask import request


def set_parsers(parsers=None):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            request.parser_classes = parsers
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def set_renderers(renderers=None):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            request.renderer_classes = renderers
            return func(*args, **kwargs)
        return decorated_function
    return decorator
