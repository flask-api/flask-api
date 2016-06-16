# coding: utf8
from __future__ import unicode_literals
from flask import request, render_template, current_app
from flask.json import JSONEncoder
from flask.globals import _request_ctx_stack
from flask_api.mediatypes import MediaType
from flask_api.compat import apply_markdown
import json
import pydoc
import re


def html_escape(text):
    escape_table = [
        ("&", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;")
    ]

    for char, replacement in escape_table:
        text = text.replace(char, replacement)
    return text


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


def convert_to_title(name):
    for char in ['-', '_', '.']:
        name = name.replace(char, ' ')
    return name.capitalize()


class BaseRenderer(object):
    media_type = None
    charset = 'utf-8'
    handles_empty_responses = False

    def render(self, data, media_type, **options):
        msg = '`render()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class JSONRenderer(BaseRenderer):
    media_type = 'application/json'
    charset = None

    def render(self, data, media_type, **options):
        # Requested indentation may be set in the Accept header.
        try:
            indent = max(min(int(media_type.params['indent']), 8), 0)
        except (KeyError, ValueError, TypeError):
            indent = None
        # Indent may be set explicitly, eg when rendered by the browsable API.
        indent = options.get('indent', indent)
        return json.dumps(data, cls=JSONEncoder, ensure_ascii=False, indent=indent)


class HTMLRenderer(object):
    media_type = 'text/html'
    charset = 'utf-8'

    def render(self, data, media_type, **options):
        return data.encode(self.charset)


class BrowsableAPIRenderer(BaseRenderer):
    media_type = 'text/html'
    handles_empty_responses = True
    template = 'base.html'

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
        if data == '' and not mock_renderer.handles_empty_responses:
            mock_content = None
        else:
            mock_content = mock_renderer.render(data, mock_media_type, indent=4)

        # Determine the allowed methods on this view.
        adapter = _request_ctx_stack.top.url_adapter
        allowed_methods = adapter.allowed_methods()

        endpoint = request.url_rule.endpoint
        view_name = str(endpoint)
        view_description = current_app.view_functions[endpoint].__doc__
        if apply_markdown is None and view_description:
            view_description = dedent(view_description)
            view_description = pydoc.html.preformat(view_description)
        elif apply_markdown is not None and view_description:
            view_description = dedent(view_description)
            view_description = apply_markdown(view_description)
        mock_content = html_escape(mock_content)

        status = options['status']
        headers = options['headers']
        headers['Content-Type'] = str(mock_media_type)

        from flask_api import __version__

        context = {
            'status': status,
            'headers': headers,
            'content': mock_content,
            'allowed_methods': allowed_methods,
            'view_name': convert_to_title(view_name),
            'view_description': view_description,
            'version': __version__
        }
        return render_template(self.template, **context)
