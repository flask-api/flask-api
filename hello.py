from flask import request
from flaskapi import FlaskAPI

app = FlaskAPI(__name__)


@app.route("/")
def hello():
    return {"foo": "Hello World!"}


if __name__ == "__main__":
    app.run(debug=True)
