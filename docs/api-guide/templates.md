# Templates

Flask API utilizes [blueprints](http://flask.pocoo.org/docs/latest/blueprints/) for managing browsable pages' template path.

Off the box, it includes a default template. But you would want to customise this for your needs.

To do that, simply copy `static` and `templates` to your project.

Then override the previous blueprint with following:

    from flask import Blueprint
    from flask_api import FlaskAPI

    theme = Blueprint(
        'flask-api', __name__,
        url_prefix='/flask-api',
        template_folder='templates', static_folder='static'
    )

    app = FlaskAPI(__name__)
    app.blueprints['flask-api'] = theme

Use `templates/base.html` as your base custom template. Note that this cannot be renamed.