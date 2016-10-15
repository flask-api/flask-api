# coding: utf8
from __future__ import unicode_literals
from flask import request, Flask, Blueprint
from flask._compat import reraise, string_types, text_type
from flask_api.exceptions import APIException
from flask_api.request import APIRequest
from flask_api.response import APIResponse
from flask_api.settings import APISettings
from itertools import chain
from werkzeug.exceptions import HTTPException
import re
import sys
from flask_api.compat import is_flask_legacy


api_resources = Blueprint(
    'flask-api', __name__,
    url_prefix='/flask-api',
    template_folder='templates', static_folder='static'
)


def urlize_quoted_links(content):
    return re.sub(r'"(https?://[^"]*)"', r'"<a href="\1">\1</a>"', content)


class FlaskAPI(Flask):
    request_class = APIRequest
    response_class = APIResponse

    def __init__(self, *args, **kwargs):
        super(FlaskAPI, self).__init__(*args, **kwargs)
        self.api_settings = APISettings(self.config)
        self.register_blueprint(api_resources)
        self.jinja_env.filters['urlize_quoted_links'] = urlize_quoted_links

    def preprocess_request(self):
        request.parser_classes = self.api_settings.DEFAULT_PARSERS
        request.renderer_classes = self.api_settings.DEFAULT_RENDERERS
        return super(FlaskAPI, self).preprocess_request()

    def make_response(self, rv):
        """
        We override this so that we can additionally handle
        list and dict types by default.
        """
        status_or_headers = headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))

        if rv is None and status_or_headers:
            raise ValueError('View function did not return a response')

        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None

        if not isinstance(rv, self.response_class):
            if isinstance(rv, (text_type, bytes, bytearray, list, dict)):
                rv = self.response_class(rv, headers=headers, status=status_or_headers)
                headers = status_or_headers = None
            else:
                rv = self.response_class.force_type(rv, request.environ)

        if status_or_headers is not None:
            if isinstance(status_or_headers, string_types):
                rv.status = status_or_headers
            else:
                rv.status_code = status_or_headers
        if headers:
            rv.headers.extend(headers)

        return rv

    def handle_user_exception(self, e):
        """
        We override the default behavior in order to deal with APIException.
        """
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        if isinstance(e, APIException):
            return self.handle_api_exception(e)

        blueprint_handlers = ()
        handlers = self.error_handler_spec.get(request.blueprint)
        if handlers is not None:
            blueprint_handlers = handlers.get(None, ())
        app_handlers = self.error_handler_spec[None].get(None, ())
        if is_flask_legacy():
            for typecheck, handler in chain(blueprint_handlers, app_handlers):
                if isinstance(e, typecheck):
                    return handler(e)
        else:
            for typecheck, handler in chain(dict(blueprint_handlers).items(),
                    dict(app_handlers).items()):
                if isinstance(e, typecheck):
                    return handler(e)

        reraise(exc_type, exc_value, tb)

    def handle_api_exception(self, exc):
        return APIResponse({'message': exc.detail}, status=exc.status_code)

    def create_url_adapter(self, request):
        """
        We need to override the default behavior slightly here,
        to ensure the any method-based routing takes account of
        any method overloading, so that eg PUT requests from the
        browsable API are routed to the correct view.
        """
        if request is not None:
            environ = request.environ.copy()
            environ['REQUEST_METHOD'] = request.method
            return self.url_map.bind_to_environ(environ,
                server_name=self.config['SERVER_NAME'])
        # We need at the very least the server name to be set for this
        # to work.
        if self.config['SERVER_NAME'] is not None:
            return self.url_map.bind(
                self.config['SERVER_NAME'],
                script_name=self.config['APPLICATION_ROOT'] or '/',
                url_scheme=self.config['PREFERRED_URL_SCHEME'])
