# coding: utf8
from __future__ import unicode_literals
from flask import request, render_template
from flask.json import JSONEncoder
from flaskapi.mediatypes import MediaType
import json


class BaseRenderer(object):
    media_type = None
    charset = 'utf-8'

    # handles_empty_responses

    def render(self, data, media_type, **options):
        msg = '`render()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class JSONRenderer(BaseRenderer):
    media_type = 'application/json'
    charset = None

    def render(self, data, media_type, **options):
        indent = options.get('indent')
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent)


class BrowsableAPIRenderer(BaseRenderer):
    media_type = 'text/html'

    def render(self, data, media_type, **options):
        # Render the content as it would have been if the client
        # had requested 'Accept: */*'.
        available_renderers = [
            renderer for renderer in request.renderer_classes
            if not issubclass(renderer, BrowsableAPIRenderer)
        ]
        assert available_renderers, 'BrowsableAPIRenderer cannot be the only renderer'
        mock_renderer = available_renderers[0]()
        mock_media_type = MediaType(mock_renderer.media_type)
        mock_content = mock_renderer.render(data, mock_media_type, indent=4)

        status = options['status']
        headers = options['headers']
        headers['Content-Type'] = str(mock_media_type)

        return render_template('base.html', status=status, headers=headers, content=mock_content)
