# coding: utf8
from __future__ import unicode_literals
from flask import abort, make_response, request
from flask_api.decorators import set_renderers
from flask_api import exceptions, renderers, status, FlaskAPI
import json
import unittest


app = FlaskAPI(__name__)
app.config['TESTING'] = True


class JSONVersion1(renderers.JSONRenderer):
    media_type = 'application/json; api-version="1.0"'


class JSONVersion2(renderers.JSONRenderer):
    media_type = 'application/json; api-version="2.0"'


@app.route('/set_status_and_headers/')
def set_status_and_headers():
    headers = {'Location': 'http://example.com/456'}
    return {'example': 'content'}, status.HTTP_201_CREATED, headers


@app.route('/set_headers/')
def set_headers():
    headers = {'Location': 'http://example.com/456'}
    return {'example': 'content'}, headers


@app.route('/make_response_view/')
def make_response_view():
    response = make_response({'example': 'content'})
    response.headers['Location'] = 'http://example.com/456'
    return response


@app.route('/api_exception/')
def api_exception():
    raise exceptions.PermissionDenied()


@app.route('/abort_view/')
def abort_view():
    abort(status.HTTP_403_FORBIDDEN)


@app.route('/accepted_media_type/')
@set_renderers([JSONVersion2, JSONVersion1])
def accepted_media_type():
    return {'accepted_media_type': str(request.accepted_media_type)}


class AppTests(unittest.TestCase):
    def test_set_status_and_headers(self):
        with app.test_client() as client:
            response = client.get('/set_status_and_headers/')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.headers['Location'], 'http://example.com/456')
            self.assertEqual(response.content_type, 'application/json')
            expected = '{"example": "content"}'
            self.assertEqual(response.get_data().decode('utf8'), expected)

    def test_set_headers(self):
        with app.test_client() as client:
            response = client.get('/set_headers/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Location'], 'http://example.com/456')
            self.assertEqual(response.content_type, 'application/json')
            expected = '{"example": "content"}'
            self.assertEqual(response.get_data().decode('utf8'), expected)

    def test_make_response(self):
        with app.test_client() as client:
            response = client.get('/make_response_view/')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.headers['Location'], 'http://example.com/456')
            self.assertEqual(response.content_type, 'application/json')
            expected = '{"example": "content"}'
            self.assertEqual(response.get_data().decode('utf8'), expected)

    def test_api_exception(self):
        with app.test_client() as client:
            response = client.get('/api_exception/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(response.content_type, 'application/json')
            expected = '{"message": "You do not have permission to perform this action."}'
            self.assertEqual(response.get_data().decode('utf8'), expected)

    def test_abort_view(self):
        with app.test_client() as client:
            response = client.get('/abort_view/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accepted_media_type_property(self):
        with app.test_client() as client:
            # Explicitly request the "api-version 1.0" renderer.
            headers = {'Accept': 'application/json; api-version="1.0"'}
            response = client.get('/accepted_media_type/', headers=headers)
            data = json.loads(response.get_data().decode('utf8'))
            expected = {'accepted_media_type': 'application/json; api-version="1.0"'}
            self.assertEqual(data, expected)

            # Request the default renderer, which is "api-version 2.0".
            headers = {'Accept': '*/*'}
            response = client.get('/accepted_media_type/', headers=headers)
            data = json.loads(response.get_data().decode('utf8'))
            expected = {'accepted_media_type': 'application/json; api-version="2.0"'}
            self.assertEqual(data, expected)
