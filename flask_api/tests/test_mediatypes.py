import unittest

from flask_api.mediatypes import MediaType, parse_accept_header


class MediaTypeParsingTests(unittest.TestCase):
    def test_media_type_with_params(self):
        media = MediaType("application/xml; schema=foobar, q=0.5")
        self.assertEqual(str(media), 'application/xml; q="0.5", schema="foobar"')
        self.assertEqual(media.main_type, "application")
        self.assertEqual(media.sub_type, "xml")
        self.assertEqual(media.full_type, "application/xml")
        self.assertEqual(media.params, {"schema": "foobar", "q": "0.5"})
        self.assertEqual(media.precedence, 3)
        self.assertEqual(
            repr(media), '<MediaType \'application/xml; q="0.5", schema="foobar"\'>'
        )

    def test_media_type_with_q_params(self):
        media = MediaType("application/xml; q=0.5")
        self.assertEqual(str(media), 'application/xml; q="0.5"')
        self.assertEqual(media.main_type, "application")
        self.assertEqual(media.sub_type, "xml")
        self.assertEqual(media.full_type, "application/xml")
        self.assertEqual(media.params, {"q": "0.5"})
        self.assertEqual(media.precedence, 2)

    def test_media_type_without_params(self):
        media = MediaType("application/xml")
        self.assertEqual(str(media), "application/xml")
        self.assertEqual(media.main_type, "application")
        self.assertEqual(media.sub_type, "xml")
        self.assertEqual(media.full_type, "application/xml")
        self.assertEqual(media.params, {})
        self.assertEqual(media.precedence, 2)

    def test_media_type_with_wildcard_sub_type(self):
        media = MediaType("application/*")
        self.assertEqual(str(media), "application/*")
        self.assertEqual(media.main_type, "application")
        self.assertEqual(media.sub_type, "*")
        self.assertEqual(media.full_type, "application/*")
        self.assertEqual(media.params, {})
        self.assertEqual(media.precedence, 1)

    def test_media_type_with_wildcard_main_type(self):
        media = MediaType("*/*")
        self.assertEqual(str(media), "*/*")
        self.assertEqual(media.main_type, "*")
        self.assertEqual(media.sub_type, "*")
        self.assertEqual(media.full_type, "*/*")
        self.assertEqual(media.params, {})
        self.assertEqual(media.precedence, 0)


class MediaTypeMatchingTests(unittest.TestCase):
    def test_media_type_includes_params(self):
        media_type = MediaType("application/json")
        other = MediaType("application/json; version=1.0")
        self.assertTrue(media_type.satisfies(other))

    def test_media_type_missing_params(self):
        media_type = MediaType("application/json; version=1.0")
        other = MediaType("application/json")
        self.assertFalse(media_type.satisfies(other))

    def test_media_type_matching_params(self):
        media_type = MediaType("application/json; version=1.0")
        other = MediaType("application/json; version=1.0")
        self.assertTrue(media_type.satisfies(other))

    def test_media_type_non_matching_params(self):
        media_type = MediaType("application/json; version=1.0")
        other = MediaType("application/json; version=2.0")
        self.assertFalse(media_type.satisfies(other))

    def test_media_type_main_type_match(self):
        media_type = MediaType("image/*")
        other = MediaType("image/png")
        self.assertTrue(media_type.satisfies(other))

    def test_media_type_sub_type_mismatch(self):
        media_type = MediaType("image/jpeg")
        other = MediaType("image/png")
        self.assertFalse(media_type.satisfies(other))

    def test_media_type_wildcard_match(self):
        media_type = MediaType("*/*")
        other = MediaType("image/png")
        self.assertTrue(media_type.satisfies(other))

    def test_media_type_wildcard_mismatch(self):
        media_type = MediaType("image/*")
        other = MediaType("audio/*")
        self.assertFalse(media_type.satisfies(other))


class AcceptHeaderTests(unittest.TestCase):
    def test_parse_simple_accept_header(self):
        parsed = parse_accept_header("*/*, application/json")
        self.assertEqual(
            parsed, [set([MediaType("application/json")]), set([MediaType("*/*")])]
        )

    def test_parse_complex_accept_header(self):
        """
        The accept header should be parsed into a list of sets of MediaType.
        The list is an ordering of precedence.

        Note that we disregard 'q' values when determining precedence, and
        instead differentiate equal values by using the server preference.
        """
        header = (
            "application/xml; schema=foo, application/json; q=0.9, application/xml, */*"
        )
        parsed = parse_accept_header(header)
        self.assertEqual(
            parsed,
            [
                set([MediaType("application/xml; schema=foo")]),
                set(
                    [MediaType("application/json; q=0.9"), MediaType("application/xml")]
                ),
                set([MediaType("*/*")]),
            ],
        )
