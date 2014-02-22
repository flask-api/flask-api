from flask import request
from flaskapi import FlaskAPI

app = FlaskAPI(__name__)


@app.route("/", methods=['GET', 'POST', 'PUT', 'DELETE'])
def example():
    return {
        "method": request.method,
        "content_type": request.content_type,
        "data": request.data
    }


if __name__ == "__main__":
    app.run(debug=True)
