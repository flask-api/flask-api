from flask import __version__ as flask_version

# Markdown is optional
try:
    import markdown
    from markdown.extensions.toc import TocExtension

    def apply_markdown(text):
        """
        Simple wrapper around :func:`markdown.markdown` to set the base level
        of '#' style headers to <h2>.
        """

        extensions = [TocExtension(baselevel=2)]
        md = markdown.Markdown(extensions=extensions)
        return md.convert(text)

except ImportError:  # pragma: no cover - markdown installed for tests
    apply_markdown = None


def is_flask_legacy():
    v = flask_version.split(".")
    return int(v[0]) == 0 and int(v[1]) < 11
