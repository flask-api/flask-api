# coding: utf8
from __future__ import unicode_literals
from flaskapi import renderers
import unittest


class RendererTests(unittest.TestCase):
    def test_render_json(self):
        renderer = renderers.JSONRenderer()
        content = renderer.render({'example': 'example'}, None)
        expected = '{"example": "example"}'
        self.assertEqual(content, expected)

    def test_renderer_negotiation_not_implemented(self):
        renderer = renderers.BaseRenderer()
        with self.assertRaises(NotImplementedError) as context:
            renderer.render(None, None)
        msg = str(context.exception)
        expected = '`render()` method must be implemented for class "BaseRenderer"'
        self.assertEqual(msg, expected)
