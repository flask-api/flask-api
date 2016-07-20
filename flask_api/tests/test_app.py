# coding: utf8
from __future__ import unicode_literals
from flask import abort, make_response, request, jsonify
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


# This is being used to test issue #58, source is taken from flask apierrors doc page
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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


@app.route('/custom_exception/')
def custom_exception():
    raise InvalidUsage('Invalid usage test.', status_code=410)


@app.route('/custom_exception_no_code/')
def custom_exception_no_status_code():
    raise InvalidUsage('Invalid usage test.')


@app.route('/abort_view/')
def abort_view():
    abort(status.HTTP_403_FORBIDDEN)


@app.route('/options/')
def options_view():
    return {}


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

    def test_custom_exception(self):
        with app.test_client() as client:
            response = client.get('/custom_exception/')
            self.assertEqual(response.status_code, status.HTTP_410_GONE)
            self.assertEqual(response.content_type, 'application/json')

    def test_custom_exception_default_code(self):
        with app.test_client() as client:
            response = client.get('/custom_exception_no_code/')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.content_type, 'application/json')

    def test_abort_view(self):
        with app.test_client() as client:
            response = client.get('/abort_view/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_options_view(self):
        with app.test_client() as client:
            response = client.options('/options/')
        # Errors if `response.response` is `None`
        response.get_data()

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
