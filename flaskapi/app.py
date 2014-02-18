# coding: utf8
from __future__ import unicode_literals
from flask import Flask
from flaskapi.request import APIRequest
from .response import APIResponse


class FlaskAPI(Flask):
    request_class = APIRequest
    response_class = APIResponse

    def make_response(self, rv):
        return self.response_class(rv)
