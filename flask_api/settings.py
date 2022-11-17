import importlib


def perform_imports(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [perform_imports(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as exc:
        format = "Could not import '%s' for API setting '%s'. %s."
        msg = format % (val, setting_name, exc)
        raise ImportError(msg)


class APISettings:
    def __init__(self, user_config=None):
        self.user_config = user_config or {}

    @property
    def DEFAULT_PARSERS(self):
        default = [
            "flask_api.parsers.JSONParser",
            "flask_api.parsers.URLEncodedParser",
            "flask_api.parsers.MultiPartParser",
        ]
        val = self.user_config.get("DEFAULT_PARSERS", default)
        return perform_imports(val, "DEFAULT_PARSERS")

    @property
    def DEFAULT_RENDERERS(self):
        default = [
            "flask_api.renderers.JSONRenderer",
            "flask_api.renderers.BrowsableAPIRenderer",
        ]
        val = self.user_config.get("DEFAULT_RENDERERS", default)
        return perform_imports(val, "DEFAULT_RENDERERS")


default_settings = APISettings()
