# coding: utf8
from __future__ import unicode_literals
from flask import request
from flask_api import exceptions
import flask_api
import io
import unittest

app = flask_api.FlaskAPI(__name__)


class MediaTypeParsingTests(unittest.TestCase):
    def test_json_request(self):
        kwargs = {
            'method': 'PUT',
            'input_stream': io.BytesIO(b'{"key": 1, "other": "two"}'),
            'content_type': 'application/json'
        }
        with app.test_request_context(**kwargs):
            self.assertEqual(request.data, {"key": 1, "other": "two"})

    def test_invalid_content_type_request(self):
        kwargs = {
            'method': 'PUT',
            'input_stream': io.BytesIO(b'Cannot parse this content type.'),
            'content_type': 'text/plain'
        }
        with app.test_request_context(**kwargs):
            with self.assertRaises(exceptions.UnsupportedMediaType):
                request.data

    def test_no_content_request(self):
        """
        Ensure that requests with no data do not populate the
        `.data`, `.form` or `.files` attributes.
        """
        with app.test_request_context(method='PUT'):
            self.assertFalse(request.data)

        with app.test_request_context(method='PUT'):
            self.assertFalse(request.form)

        with app.test_request_context(method='PUT'):
            self.assertFalse(request.files)

    def test_encode_request(self):
        """
        Ensure that `.full_path` is correctly decoded in python 3
        """
        with app.test_request_context(method='GET', path='/?a=b'):
            self.assertEqual(request.full_path, '/?a=b')
