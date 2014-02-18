# coding: utf8
from __future__ import unicode_literals
from flask import abort, make_response
from flaskapi import exceptions, status, FlaskAPI
import unittest


app = FlaskAPI(__name__)


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
    response.headers = {'Location': 'http://example.com/456'}
    return response


@app.route('/api_exception/')
def api_exception():
    raise exceptions.PermissionDenied()


@app.route('/abort_view/')
def abort_view():
    abort(status.HTTP_403_FORBIDDEN)


class ParserTests(unittest.TestCase):
    def test_set_status_and_headers(self):
        with app.test_client() as client:
            response = client.get('/set_status_and_headers/')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.headers['Location'], 'http://example.com/456')

    def test_set_headers(self):
        with app.test_client() as client:
            response = client.get('/set_headers/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Location'], 'http://example.com/456')

    def test_make_response(self):
        with app.test_client() as client:
            response = client.get('/make_response_view/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.headers['Location'], 'http://example.com/456')

    def test_api_exception(self):
        with app.test_client() as client:
            response = client.get('/api_exception/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(response.get_data().decode('utf8'), '{"message": "You do not have permission to perform this action."}')

    def test_abort_view(self):
        with app.test_client() as client:
            response = client.get('/abort_view/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
