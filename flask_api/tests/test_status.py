# coding: utf8
from __future__ import unicode_literals
from flask_api import status
import unittest


class TestStatus(unittest.TestCase):
    def test_status_categories(self):
        self.assertFalse(status.is_informational(99))
        self.assertTrue(status.is_informational(100))
        self.assertTrue(status.is_informational(199))
        self.assertFalse(status.is_informational(200))

        self.assertFalse(status.is_success(199))
        self.assertTrue(status.is_success(200))
        self.assertTrue(status.is_success(299))
        self.assertFalse(status.is_success(300))

        self.assertFalse(status.is_redirect(299))
        self.assertTrue(status.is_redirect(300))
        self.assertTrue(status.is_redirect(399))
        self.assertFalse(status.is_redirect(400))

        self.assertFalse(status.is_client_error(399))
        self.assertTrue(status.is_client_error(400))
        self.assertTrue(status.is_client_error(499))
        self.assertFalse(status.is_client_error(500))

        self.assertFalse(status.is_server_error(499))
        self.assertTrue(status.is_server_error(500))
        self.assertTrue(status.is_server_error(599))
        self.assertFalse(status.is_server_error(600))
