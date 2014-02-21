# coding: utf8
from __future__ import unicode_literals
from flask import request, render_template, current_app
from flask.json import JSONEncoder
from flask.globals import _request_ctx_stack
from flaskapi.mediatypes import MediaType
import json
import re


def dedent(content):
    """
    Remove leading indent from a block of text.
    Used when generating descriptions from docstrings.

    Note that python's `textwrap.dedent` doesn't quite cut it,
    as it fails to dedent multiline docstrings that include
    unindented text on the initial line.
    """
    whitespace_counts = [len(line) - len(line.lstrip(' '))
                         for line in content.splitlines()[1:] if line.lstrip()]

    # unindent the content if needed
    if whitespace_counts:
        whitespace_pattern = '^' + (' ' * min(whitespace_counts))
        content = re.sub(re.compile(whitespace_pattern, re.MULTILINE), '', content)

    return content.strip()


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

        # Determine the allowed methods on this view.
        adapter = _request_ctx_stack.top.url_adapter
        allowed_methods = adapter.allowed_methods()

        endpoint = request.url_rule.endpoint
        view_name = str(endpoint)
        view_description = current_app.view_functions[endpoint].__doc__
        if view_description is not None:
            view_description = dedent(view_description)

        status = options['status']
        headers = options['headers']
        headers['Content-Type'] = str(mock_media_type)

        from flaskapi import __version__

        context = {
            'status': status,
            'headers': headers,
            'content': mock_content,
            'allowed_methods': allowed_methods,
            'view_name': view_name,
            'view_description': view_description,
            'version': __version__
        }
        return render_template('base.html', **context)
