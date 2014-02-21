# coding: utf8
from __future__ import unicode_literals
from flask import Request
from flaskapi.negotiation import DefaultNegotiation
from flaskapi.settings import default_settings
from werkzeug.datastructures import MultiDict
from werkzeug.wsgi import get_content_length


class APIRequest(Request):
    parser_classes = default_settings.DEFAULT_PARSERS
    renderer_classes = default_settings.DEFAULT_RENDERERS
    negotiator_class = DefaultNegotiation
    empty_data_class = MultiDict

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._parse()
        return self._data

    @property
    def form(self):
        if not hasattr(self, '_form'):
            self._parse()
        return self._form

    @property
    def files(self):
        if not hasattr(self, '_files'):
            self._parse()
        return self._files

    @property
    def accepted_renderer(self):
        if not hasattr(self, '_accepted_renderer'):
            self._perform_content_negotiation()
        return self._accepted_renderer

    @property
    def accepted_media_type(self):
        if not hasattr(self, '_accepted_media_type'):
            self._perform_content_negotiation()
        return self._accepted_media_type

    def _parse(self):
        content_length = get_content_length(self.environ)
        content_type = self.environ.get('CONTENT_TYPE')

        if not content_type or not content_length:
            self._set_empty_data()
            return

        negotiator = self.negotiator_class()
        parsers = [parser_cls() for parser_cls in self.parser_classes]
        options = self._get_parser_options()
        try:
            parser, media_type = negotiator.select_parser(parsers)
            ret = parser.parse(self.stream, media_type, **options)
        except:
            # Ensure that accessing `request.data` again does not reraise
            # the exception, so that eg exceptions can handle properly.
            self._set_empty_data()
            raise

        if parser.handles_file_uploads:
            assert isinstance(ret, tuple) and len(ret) == 2, 'Expected a two-tuple of (data, files)'
            self._data, self._files = ret
        else:
            self._data = ret
            self._files = self.empty_data_class()

        self._form = self._data if parser.handles_form_data else self.empty_data_class()

    def _get_parser_options(self):
        return {'content_length': get_content_length(self.environ)}

    def _set_empty_data(self):
        self._data = self.empty_data_class()
        self._form = self.empty_data_class()
        self._files = self.empty_data_class()

    def _perform_content_negotiation(self):
        negotiator = self.negotiator_class()
        renderers = [renderer() for renderer in self.renderer_classes]
        self._accepted_renderer, self._accepted_media_type = negotiator.select_renderer(renderers)

    @property
    def full_path(self):
        if not self.query_string:
            return self.path
        return self.path + u'?' + self.query_string

    # @property
    # def auth(self):
    #     if not has_attribute(self, '_auth'):
    #         self._authenticate()
    #     return self._auth

    # def _authenticate(self):
    #     for authentication_class in self.authentication_classes:
    #         authenticator = authentication_class()
    #         try:
    #             auth = authenticator.authenticate(self)
    #         except exceptions.APIException:
    #             self._not_authenticated()
    #             raise

    #         if not auth is None:
    #             self._authenticator = authenticator
    #             self._auth = auth
    #             return

    #     self._not_authenticated()

    # def _not_authenticated(self):
    #     self._authenticator = None
    #     self._auth = None
