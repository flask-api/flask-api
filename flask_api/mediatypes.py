# coding: utf8
from __future__ import unicode_literals


class MediaType(object):
    def __init__(self, media_type):
        self.main_type, self.sub_type, self.params = self._parse(media_type)

    @property
    def full_type(self):
        return self.main_type + '/' + self.sub_type

    @property
    def precedence(self):
        """
        Precedence is determined by how specific a media type is:

        3. 'type/subtype; param=val'
        2. 'type/subtype'
        1. 'type/*'
        0. '*/*'
        """
        if self.main_type == '*':
            return 0
        elif self.sub_type == '*':
            return 1
        elif not self.params or list(self.params.keys()) == ['q']:
            return 2
        return 3

    def satisfies(self, other):
        """
        Returns `True` if this media type is a superset of `other`.
        Some examples of cases where this holds true:

        'application/json; version=1.0' >= 'application/json; version=1.0'
        'application/json'              >= 'application/json; indent=4'
        'text/*'                        >= 'text/plain'
        '*/*'                           >= 'text/plain'
        """
        for key in self.params.keys():
            if key != 'q' and other.params.get(key, None) != self.params.get(key, None):
                return False

        if self.sub_type != '*' and other.sub_type != '*' and other.sub_type != self.sub_type:
            return False

        if self.main_type != '*' and other.main_type != '*' and other.main_type != self.main_type:
            return False

        return True

    def _parse(self, media_type):
        """
        Parse a media type string, like "application/json; indent=4" into a
        three-tuple, like: ('application', 'json', {'indent': 4})
        """
        full_type, sep, param_string = media_type.partition(';')
        params = {}
        for token in param_string.strip().split(','):
            key, sep, value = [s.strip() for s in token.partition('=')]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if key:
                params[key] = value
        main_type, sep, sub_type = [s.strip() for s in full_type.partition('/')]
        return (main_type, sub_type, params)

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, str(self))

    def __str__(self):
        """
        Return a canonical string representing the media type.
        Note that this ensures the params are sorted.
        """
        if self.params:
            params_str = ', '.join([
                '%s="%s"' % (key, val)
                for key, val in sorted(self.params.items())
            ])
            return self.full_type + '; ' + params_str
        return self.full_type

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        # Compare two MediaType instances, ignoring parameter ordering.
        return (
            self.full_type == other.full_type and self.params == other.params
        )


def parse_accept_header(accept):
    """
    Parses the value of a clients accept header, and returns a list of sets
    of media types it included, ordered by precedence.

    For example, 'application/json, application/xml, */*' would return:

    [
        set([<MediaType "application/xml">, <MediaType "application/json">]),
        set([<MediaType "*/*">])
    ]
    """
    ret = [set(), set(), set(), set()]
    for token in accept.split(','):
        media_type = MediaType(token.strip())
        ret[3 - media_type.precedence].add(media_type)
    return [media_types for media_types in ret if media_types]
