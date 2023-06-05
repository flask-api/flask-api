import unittest

from flask_api import exceptions, status


class Conflict(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Could not update the resource"


class TestExceptions(unittest.TestCase):
    def test_custom_exception(self):
        try:
            raise Conflict()
        except Conflict as exc:
            self.assertEqual(str(exc), "Could not update the resource")
            self.assertEqual(exc.status_code, 409)

    def test_override_exception_detail(self):
        try:
            raise Conflict("A widget with this id already exists")
        except Conflict as exc:
            self.assertEqual(str(exc), "A widget with this id already exists")
            self.assertEqual(exc.status_code, 409)
