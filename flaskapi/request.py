# coding: utf8
from __future__ import unicode_literals
from flask import Request
from flaskapi.parsers import JSONParser
from flaskapi.negotiation import DefaultNegotiation
from werkzeug.datastructures import MultiDict
from werkzeug.wsgi import get_content_length


class APIRequest(Request):
    parser_classes = [JSONParser]
    negotiator_class = DefaultNegotiation
    empty_data_class = MultiDict

    @property
    def has_content(self):
        return self.environ.get('CONTENT_TYPE') and get_content_length(self.environ)

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = self._parse()
        return self._data

    def _parse(self):
        if not self.has_content:
            self._data = self.empty_data_class()
            return

        negotiator = self.negotiator_class()
        parsers = [parser_cls() for parser_cls in self.parser_classes]

        try:
            parser, media_type = negotiator.select_parser(parsers)
            return parser.parse(self.stream, media_type)
        except:
            self._data = self.empty_data_class()
            raise

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
