# coding: utf8
from __future__ import unicode_literals
from flask import request
from flask_api import exceptions
from flask_api.mediatypes import MediaType, parse_accept_header


class BaseNegotiation(object):
    def select_parser(self, parsers):
        msg = '`select_parser()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)

    def select_renderer(self, renderers):
        msg = '`select_renderer()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class DefaultNegotiation(BaseNegotiation):
    def select_parser(self, parsers):
        """
        Determine which parser to use for parsing the request body.
        Returns a two-tuple of (parser, content type).
        """
        content_type_header = request.content_type

        client_media_type = MediaType(content_type_header)
        for parser in parsers:
            server_media_type = MediaType(parser.media_type)
            if server_media_type.satisfies(client_media_type):
                return (parser, client_media_type)

        raise exceptions.UnsupportedMediaType()

    def select_renderer(self, renderers):
        """
        Determine which renderer to use for rendering the response body.
        Returns a two-tuple of (renderer, content type).
        """
        accept_header = request.headers.get('Accept', '*/*')

        for client_media_types in parse_accept_header(accept_header):
            for renderer in renderers:
                server_media_type = MediaType(renderer.media_type)
                for client_media_type in client_media_types:
                    if client_media_type.satisfies(server_media_type):
                        if server_media_type.precedence > client_media_type.precedence:
                            return (renderer, server_media_type)
                        else:
                            return (renderer, client_media_type)

        raise exceptions.NotAcceptable()
