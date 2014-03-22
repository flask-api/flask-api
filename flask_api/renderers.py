# coding: utf8
from __future__ import unicode_literals
from flask import request, render_template, current_app
from flask._compat import string_types
from flask.json import JSONEncoder
from flask.globals import _request_ctx_stack
from flask_api.mediatypes import MediaType
import json
import re
import sys


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
    return name.replace('-', ' ').replace('_', ' ').capitalize()


def detect_module_encoding(mod):
    """Detect the character encoding of the given module

    :param module mod: a module to detect its encoding.
    :return: a name of detected encoding, or `None` if unknown
    :rtype: str | None

    .. seealso:: :pep:`0263`

    .. warning::

       This function might not work with the situation that there is no source
       file of given module. For example, zipped egg distributions will cause
       that problem.

    """
    if isinstance(mod, string_types):
        mod = sys.modules[mod]
    filepath = mod.__file__
    if filepath.endswith('.pyc'):
        filepath = filepath[:-1]
    with open(filepath) as f:
        for i, line in enumerate(f):
            if i >= 2:
                break
            m = re.search(r'#.*coding[:=]\s*([-\w.]+)', line)
            assert m
            if m:
                return m.group(1)
    return None


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
        view_function = current_app.view_functions[endpoint]
        view_description = view_function.__doc__
        if view_description is not None:
            try:
                view_description = dedent(view_description)
            except UnicodeDecodeError:
                encoding = detect_module_encoding(view_function.__module__)
                view_description = view_description.decode(encoding)
                view_description = dedent(view_description)

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
        return render_template('base.html', **context)
