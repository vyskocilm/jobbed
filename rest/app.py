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

@app.route ("/api/v0.1/scripts", methods=["GET"])
def get_scripts ():
    """Return the list of resume scripts available on the system"""
    return make_response (
        jsonify ({"scripts": [
            {"script" : "jobbed_html", "Content-type" : "text/html; charset=utf-8"},
            {"script" : "jobbed_latex", "Content-type" : "text/plain; charset=utf-8"}]}),
        http.HTTPStatus.NOT_IMPLEMENTED)


@app.route ("/api/v0.1/scripts/<script>", methods=["POST"])
def post_resume (script):
    # 1. get the 
    return make_response (
            jsonify ({"error" : "Not yet implemented: " + script}),
        http.HTTPStatus.NOT_IMPLEMENTED)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
