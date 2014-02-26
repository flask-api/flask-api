# coding: utf8
from __future__ import unicode_literals
import unittest
import flask_api
from flask_api import exceptions
from flask_api.negotiation import BaseNegotiation, DefaultNegotiation


app = flask_api.FlaskAPI(__name__)


class JSON(object):
    media_type = 'application/json'


class HTML(object):
    media_type = 'application/html'


class URLEncodedForm(object):
    media_type = 'application/x-www-form-urlencoded'


class TestRendererNegotiation(unittest.TestCase):
    def test_select_renderer_client_preference(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': 'application/html'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_renderer(renderers)
            self.assertEqual(renderer, HTML)
            self.assertEqual(str(media_type), 'application/html')

    def test_select_renderer_no_accept_header(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        with app.test_request_context():
            renderer, media_type = negotiation.select_renderer(renderers)
            self.assertEqual(renderer, JSON)
            self.assertEqual(str(media_type), 'application/json')

    def test_select_renderer_server_preference(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': '*/*'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_renderer(renderers)
            self.assertEqual(renderer, JSON)
            self.assertEqual(str(media_type), 'application/json')

    def test_select_renderer_failed(self):
        negotiation = DefaultNegotiation()
        renderers = [JSON, HTML]
        headers = {'Accept': 'application/xml'}
        with app.test_request_context(headers=headers):
            with self.assertRaises(exceptions.NotAcceptable):
                renderer, media_type = negotiation.select_renderer(renderers)

    def test_renderer_negotiation_not_implemented(self):
        negotiation = BaseNegotiation()
        with self.assertRaises(NotImplementedError) as context:
            negotiation.select_renderer([])
        msg = str(context.exception)
        expected = '`select_renderer()` method must be implemented for class "BaseNegotiation"'
        self.assertEqual(msg, expected)


class TestParserNegotiation(unittest.TestCase):
    def test_select_parser(self):
        negotiation = DefaultNegotiation()
        parsers = [JSON, URLEncodedForm]
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        with app.test_request_context(headers=headers):
            renderer, media_type = negotiation.select_parser(parsers)
            self.assertEqual(renderer, URLEncodedForm)
            self.assertEqual(str(media_type), 'application/x-www-form-urlencoded')

    def test_select_parser_failed(self):
        negotiation = DefaultNegotiation()
        parsers = [JSON, URLEncodedForm]
        headers = {'Content-Type': 'application/xml'}
        with app.test_request_context(headers=headers):
            with self.assertRaises(exceptions.UnsupportedMediaType):
                renderer, media_type = negotiation.select_parser(parsers)

    def test_parser_negotiation_not_implemented(self):
        negotiation = BaseNegotiation()
        with self.assertRaises(NotImplementedError) as context:
            negotiation.select_parser([])
        msg = str(context.exception)
        expected = '`select_parser()` method must be implemented for class "BaseNegotiation"'
        self.assertEqual(msg, expected)
