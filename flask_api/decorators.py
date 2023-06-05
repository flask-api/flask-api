from functools import wraps

from flask import request


def set_parsers(*parsers):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if len(parsers) == 1 and isinstance(parsers[0], (list, tuple)):
                request.parser_classes = parsers[0]
            else:
                request.parser_classes = parsers
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def set_renderers(*renderers):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if len(renderers) == 1 and isinstance(renderers[0], (list, tuple)):
                request.renderer_classes = renderers[0]
            else:
                request.renderer_classes = renderers
            return func(*args, **kwargs)

        return decorated_function

    return decorator
