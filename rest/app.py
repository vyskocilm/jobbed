#!flask/bin/python

import http # and now we REQUIRE python3

from flask import Flask, jsonify, make_response

app = Flask(__name__)

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Jobbed welcome</title>
    </head>

    <body>
    There is NOTHING here right now!
    </body>

</html>
"""

@app.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify({"error": "Not found"}),
        http.HTTPStatus.NOT_FOUND)

@app.route ("/api/v0.1/resume", methods=["POST"])
def post_resume ():
    return make_response (
        jsonify ({"error" : "Not yet implemented"}),
        http.HTTPStatus.NOT_IMPLEMENTED)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
