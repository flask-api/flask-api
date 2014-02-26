# coding: utf8
from __future__ import unicode_literals
from flask_api.settings import APISettings
import unittest


class SettingsTests(unittest.TestCase):
    def test_bad_import(self):
        settings = APISettings({'DEFAULT_PARSERS': 'foobarz.FailedImport'})
        with self.assertRaises(ImportError) as context:
            settings.DEFAULT_PARSERS
        msg = str(context.exception)
        excepted_py2 = (
            "Could not import 'foobarz.FailedImport' for API setting "
            "'DEFAULT_PARSERS'. No module named foobarz."
        )
        excepted_py3 = (
            "Could not import 'foobarz.FailedImport' for API setting "
            "'DEFAULT_PARSERS'. No module named 'foobarz'."
        )
        self.assertIn(msg, (excepted_py2, excepted_py3))
