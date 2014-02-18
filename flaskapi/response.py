# coding: utf8
from __future__ import unicode_literals
from flask import Response
from flaskapi.renderers import JSONRenderer
from flaskapi.negotiation import DefaultNegotiation


class APIResponse(Response):
    renderer_classes = [JSONRenderer]
    negotiator_class = DefaultNegotiation

    def __init__(self, content, *args, **kwargs):
        media_type = None
        if isinstance(content, (list, dict)):
            negotiator = self.negotiator_class()
            renderers = [renderer() for renderer in self.renderer_classes]
            renderer, media_type = negotiator.select_renderer(renderers)
            content = renderer.render(content, media_type)

        super(APIResponse, self).__init__(content, *args, **kwargs)

        if media_type is not None:
            self.headers['Content-Type'] = media_type
