# coding: utf8
from __future__ import unicode_literals
from flask.json import JSONEncoder
from flask._compat import text_type
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
    encoder_class = JSONEncoder
    ensure_ascii = False

    def render(self, data, media_type):
        ret = json.dumps(data, cls=self.encoder_class, ensure_ascii=self.ensure_ascii)

        # On python 2.x json.dumps() returns bytestrings if ensure_ascii=True,
        # but if ensure_ascii=False, the return type is underspecified,
        # and may (or may not) be unicode.
        # On python 3.x json.dumps() returns unicode strings.
        if isinstance(ret, text_type):
            return bytes(ret.encode('utf-8'))
        return ret
