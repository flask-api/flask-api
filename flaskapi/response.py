# coding: utf8
from __future__ import unicode_literals
from flask import Response
from flaskapi.renderers import JSONRenderer
from flaskapi.negotiation import DefaultNegotiation


class APIResponse(Response):
    renderer_classes = [JSONRenderer]
    negotiator_class = DefaultNegotiation

    def __init__(self, content, *args, **kwargs):
        super(APIResponse, self).__init__(None, *args, **kwargs)
        self._content = content

    def render(self):
        if self._content is None:
            self.response = []
            return

        negotiator = self.negotiator_class()
        renderers = [renderer() for renderer in self.renderer_classes]
        renderer, media_type = negotiator.select_renderer(renderers)

        response = renderer.render(self._content, media_type)
        if response is None:
            self.response = []
        else:
            self.set_data(response)
            self.headers['Content-Type'] = str(media_type)
