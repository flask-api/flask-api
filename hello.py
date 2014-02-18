from flask import request
from flaskapi import FlaskAPI

app = FlaskAPI(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello():
    return {"foo": request.data}


if __name__ == "__main__":
    app.run(debug=True)
