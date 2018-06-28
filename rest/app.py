#!flask/bin/python

import http # and now we REQUIRE python3

from flask import Flask, jsonify, make_response

app = Flask(__name__)

def call_pdflatex ():
    pass

def call_gsl ():
    pass

def make_jresponse (obj, return_code=http.HTTPStatus.OK):
    return make_response (jsonify (obj), return_code)

class Scripts:

    def __init__ (self):
        self._scripts = {
            "latex" : 
                {"path" : "../jobbed_latex.gsl",
                 "description" : "LaTeX output",
                 "code" : call_pdflatex},
            "html" :
                {"path" : "../jobbed_html.gsl",
                 "description" : "plain HTML5 output",
                 "code" : call_gsl},
        }

        self._rest = [{"script" : script, "description" : value ["description"]} for
                script, value in self._scripts.items ()]

    @property
    def rest (self):
        return self._rest

    def __in__ (self, script):
        return script in self._scripts

    def __getitem__ (self, script):
        return self._scripts [script]

SCRIPTS = Scripts ()

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

    global SCRIPTS
    return make_response (
            jsonify ({"scripts": SCRIPTS.rest}),
            http.HTTPStatus.OK)

@app.route ("/api/v0.1/scripts/<script>", methods=["GET"])
def get_scripts_script (script):

    global SCRIPTS
    try:
        return make_jresponse (
            {"script" : script,
             "description": SCRIPTS [script]["description"]})
    except KeyError:
        return make_jresponse (
            {"error" : "Not found script '%s'" % script},
            http.HTTPStatus.NOT_FOUND)


@app.route ("/api/v0.1/scripts/<script>", methods=["POST"])
def post_resume (script):
    global SCRIPTS
    return make_response (
            jsonify ({"error" : "Not yet implemented: " + script}),
        http.HTTPStatus.NOT_IMPLEMENTED)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
