# coding: utf8
from __future__ import unicode_literals
from flaskapi import exceptions, parsers
import io
import unittest


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
            parser.parse(stream, 'application/json')
        detail = str(context.exception)
        expected_py2 = 'JSON parse error - Expecting property name: line 1 column 1 (char 1)'
        expected_py3 = 'JSON parse error - Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'
        self.assertIn(detail, (expected_py2, expected_py3))

    def test_renderer_negotiation_not_implemented(self):
        parser = parsers.BaseParser()
        with self.assertRaises(NotImplementedError) as context:
            parser.parse(None, None)
        msg = str(context.exception)
        expected = '`parse()` method must be implemented for class "BaseParser"'
        self.assertEqual(msg, expected)
