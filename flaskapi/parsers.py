# coding: utf8
from __future__ import unicode_literals
from flask._compat import text_type
from flaskapi import exceptions
import json


class BaseParser(object):
    media_type = None

    def parse(self, stream, media_type):
        msg = '`parse()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class JSONParser(BaseParser):
    media_type = 'application/json'

    def parse(self, stream, media_type):
        try:
            data = stream.read().decode('utf-8')
            return json.loads(data)
        except ValueError as exc:
            msg = 'JSON parse error - %s' % text_type(exc)
            raise exceptions.ParseError(msg)
