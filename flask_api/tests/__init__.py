# This is a fudge that allows us to easily specify test modules.
# For example:
# ./runtests test_parsers
# ./runtests test_renderers.RendererTests.test_render_json
import os

modules = [
    filename.rsplit(".", 1)[0]
    for filename in os.listdir(os.path.dirname(__file__))
    if filename.endswith(".py") and filename.startswith("test_")
]

for module in modules:
    exec("from flask_api.tests.%s import *" % module)
