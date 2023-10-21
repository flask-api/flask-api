import json

from werkzeug.formparser import MultiPartParser as WerkzeugMultiPartParser
from werkzeug.formparser import default_stream_factory

from flask_api.helpers import url_decode_stream
from flask_api import exceptions


class BaseParser:
    media_type = None
    handles_file_uploads = False  # If set then 'request.files' will be populated.
    handles_form_data = False  # If set then 'request.form' will be populated.

    def parse(self, stream, media_type, **options):
        msg = '`parse()` method must be implemented for class "%s"'
        raise NotImplementedError(msg % self.__class__.__name__)


class JSONParser(BaseParser):
    media_type = "application/json"

    def parse(self, stream, media_type, **options):
        data = stream.read().decode("utf-8")
        try:
            return json.loads(data)
        except ValueError as exc:
            msg = "JSON parse error - %s" % str(exc)
            raise exceptions.ParseError(msg)


class MultiPartParser(BaseParser):
    media_type = "multipart/form-data"
    handles_file_uploads = True
    handles_form_data = True

    def parse(self, stream, media_type, **options):
        boundary = media_type.params.get("boundary")
        if boundary is None:
            msg = "Multipart message missing boundary in Content-Type header"
            raise exceptions.ParseError(msg)
        boundary = boundary.encode("ascii")

        content_length = options.get("content_length")
        assert (
            content_length is not None
        ), "MultiPartParser.parse() requires `content_length` argument"

        buffer_size = content_length
        while buffer_size % 4 or buffer_size < 1024:
            buffer_size += 1
        multipart_parser = WerkzeugMultiPartParser(
            default_stream_factory, buffer_size=buffer_size
        )

        try:
            return multipart_parser.parse(stream, boundary, content_length)
        except ValueError as exc:
            msg = "Multipart parse error - %s" % str(exc)
            raise exceptions.ParseError(msg)


class URLEncodedParser(BaseParser):
    media_type = "application/x-www-form-urlencoded"
    handles_form_data = True

    def parse(self, stream, media_type, **options):
        return url_decode_stream(stream)
