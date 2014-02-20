# coding: utf8
from __future__ import unicode_literals
from flask import request, Response
from flask._compat import text_type


class APIResponse(Response):
    def __init__(self, content, *args, **kwargs):
        super(APIResponse, self).__init__(None, *args, **kwargs)

        media_type = None
        if isinstance(content, (list, dict, text_type)):
            renderer = request.accepted_renderer
            media_type = request.accepted_media_type
            options = self.get_renderer_options()
            content = renderer.render(content, media_type, **options)

        if isinstance(content, (text_type, bytes, bytearray)):
            self.set_data(content)
        else:
            self.response = content

        if media_type is not None:
            self.headers['Content-Type'] = media_type

    def get_renderer_options(self):
        return {
            'status': self.status,
            'status_code': self.status_code,
            'headers': self.headers
        }
