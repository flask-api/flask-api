# coding: utf8
from __future__ import unicode_literals
from flask.json import JSONEncoder
import json


class BaseRenderer(object):
    media_type = None
    charset = 'utf-8'

    # handles_empty_responses
    # handles_form
    # handles_files

    def render(self, data, media_type):
        msg = '`render()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class JSONRenderer(BaseRenderer):
    media_type = 'application/json'
    charset = None

    def render(self, data, media_type):
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False)
