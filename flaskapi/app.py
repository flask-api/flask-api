# coding: utf8
from __future__ import unicode_literals
from flask import Flask
from flaskapi.request import APIRequest
from .response import APIResponse


class FlaskAPI(Flask):
    request_class = APIRequest
    response_class = APIResponse

    # def preprocess_request(self):
    #     return super(FlaskAPI, self).preprocess_request()

    def process_response(self, response):
        response = super(FlaskAPI, self).process_response(response)
        if isinstance(response, APIResponse):
            response.render()
        return response

    def make_response(self, rv):
        return self.response_class(rv)
