def url_decode_stream(stream):
    import urllib
    body = stream.read()
    body_str = body.decode()
    return dict(urllib.parse.parse_qsl(body_str))
