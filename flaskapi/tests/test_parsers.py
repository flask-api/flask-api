# coding: utf8
from __future__ import unicode_literals
from flask import request
from flaskapi import exceptions, parsers, status, mediatypes, FlaskAPI
import io
import json
import unittest


app = FlaskAPI(__name__)


@app.route('/', methods=['POST'])
def data():
    return {
        'data': request.data,
        'form': request.form,
        'files': dict([
            (key, {'name': val.filename, 'contents': val.read().decode('utf8')})
            for key, val in request.files.items()
        ])
    }


class ParserTests(unittest.TestCase):
    def test_valid_json(self):
        parser = parsers.JSONParser()
        stream = io.BytesIO(b'{"key": 1, "other": "two"}')
        data = parser.parse(stream, 'application/json')
        self.assertEqual(data, {"key": 1, "other": "two"})

    def test_invalid_json(self):
        parser = parsers.JSONParser()
        stream = io.BytesIO(b'{key: 1, "other": "two"}')
        with self.assertRaises(exceptions.ParseError) as context:
            parser.parse(stream, mediatypes.MediaType('application/json'))
        detail = str(context.exception)
        expected_py2 = 'JSON parse error - Expecting property name: line 1 column 1 (char 1)'
        expected_py3 = 'JSON parse error - Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'
        self.assertIn(detail, (expected_py2, expected_py3))

    def test_invalid_multipart(self):
        parser = parsers.MultiPartParser()
        stream = io.BytesIO(b'invalid')
        with self.assertRaises(exceptions.ParseError) as context:
            parser.parse(stream, mediatypes.MediaType('multipart/form-data; boundary="foo"'))
        detail = str(context.exception)
        expected = 'Multipart parse error - Expected boundary at start of multipart data'
        self.assertEqual(detail, expected)

    def test_invalid_multipart_no_boundary(self):
        parser = parsers.MultiPartParser()
        stream = io.BytesIO(b'invalid')
        with self.assertRaises(exceptions.ParseError) as context:
            parser.parse(stream, mediatypes.MediaType('multipart/form-data'))
        detail = str(context.exception)
        expected = 'Multipart message missing boundary in Content-Type header'
        self.assertEqual(detail, expected)

    def test_renderer_negotiation_not_implemented(self):
        parser = parsers.BaseParser()
        with self.assertRaises(NotImplementedError) as context:
            parser.parse(None, None)
        msg = str(context.exception)
        expected = '`parse()` method must be implemented for class "BaseParser"'
        self.assertEqual(msg, expected)

    def test_accessing_json(self):
        with app.test_client() as client:
            data = json.dumps({'example': 'example'})
            response = client.post('/', data=data, content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            data = json.loads(response.get_data().decode('utf8'))
            expected = {
                "data": {"example": "example"},
                "form": {},
                "files": {}
            }
            self.assertEqual(data, expected)

    def test_accessing_url_encoded(self):
        with app.test_client() as client:
            data = {'example': 'example'}
            response = client.post('/', data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            data = json.loads(response.get_data().decode('utf8'))
            expected = {
                "data": {"example": "example"},
                "form": {"example": "example"},
                "files": {}
            }
            self.assertEqual(data, expected)

    def test_accessing_multipart(self):
        with app.test_client() as client:
            data = {'example': 'example', 'upload': (io.BytesIO(b'file contents'), 'name.txt')}
            response = client.post('/', data=data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            data = json.loads(response.get_data().decode('utf8'))
            expected = {
                "data": {"example": "example"},
                "form": {"example": "example"},
                "files": {"upload": {"name": "name.txt", "contents": "file contents"}}
            }
            self.assertEqual(data, expected)
