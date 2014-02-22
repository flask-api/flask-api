from flask import request
from flaskapi import FlaskAPI, status, exceptions

app = FlaskAPI(__name__)


notes = {
    0: {'text': 'do the shopping'},
    1: {'text': 'build the codez'},
    2: {'text': 'paint the door'},
}


@app.route("/", methods=['GET', 'POST'])
def notes_list():
    if request.method == 'POST':
        note = {'text': str(request.data.get('text', ''))}
        idx = max(notes.keys()) + 1
        notes[idx] = note
        return note, status.HTTP_201_CREATED

    # request.method == 'GET'
    return notes


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def notes_detail(key):
    if request.method == 'PUT':
        note = {'text': str(request.data.get('text', ''))}
        notes[key] = note
        return note

    elif request.method == 'DELETE':
        notes.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if key not in notes:
        raise exceptions.NotFound()
    return notes[key]


if __name__ == "__main__":
    app.run(debug=True)
