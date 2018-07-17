#!flask/bin/python

import http # and now we REQUIRE python3

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import url_for
from flask import request
import xml.etree.ElementTree as ET
import tempfile
import os
from functools import partial as FP
import uuid
import subprocess

app = Flask(__name__)
CWD = os.getcwd ()

def make_jresponse (obj, return_code=http.HTTPStatus.OK):
    return make_response (jsonify (obj), return_code)

def call_gsl (cwd, script, output_name):
    subprocess.check_call (["gsl", f"-script:{cwd}/../{script}.gsl", "resume.xml"])
    #TODO: assert is exists and if is valid
    return output_name

def call_pdflatex ():
    raise NotImplementedError

# main business logic code
def do_jobbed (xml, code):
    global CWD
    #TODO: add an extra validation of loaded XML
    #TODO: this MUST be isolated from main server
    workdir = tempfile.TemporaryDirectory (
        prefix="jobbed",
        dir=os.path.join (CWD, "workdir"))

    cwd = CWD
    os.chdir (workdir.name)

    with open ("resume.xml", "wb") as resume_file:
        resume_file.write (ET.tostring (xml))

    _uuid = str (uuid.uuid4 ())
    os.makedirs (
        os.path.join (
            cwd,
            "static",
            _uuid))

    if not isinstance (code, tuple):
        code = (code, )

    outputs = []
    #FIXME: error handling
    for f in code:
        out = f ()
        os.rename (out,
            os.path.join (
                cwd,
                "static",
                _uuid,
                out))
        outputs.append (
            url_for ("static", filename=f"{_uuid}/{out}"))

    os.chdir (cwd)
    workdir.cleanup ()

    return outputs, http.HTTPStatus.OK

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


# List of scripts
SCRIPTS = {
    "jobbed_html" : {
        "path" : "jobbed_html.gsl",
        "description" : "Create plain html5 output",
        "code" : (FP (call_gsl, CWD, "jobbed_html", "resume.html"), )
    },
    "jobbed_latex" : {
        "path" : "jobbed_latex.gsl",
        "description" : "Create LaTeX and PDF output",
        "code" : call_pdflatex
    },
}

@app.route ("/api/v1/scripts", methods=["GET"])
def get_scripts ():
    return make_jresponse ([
        {
            "id" : name,
            "api" : url_for ("post_scripts", name=name),
            "description": script["description"],
        }
        for name, script in SCRIPTS.items ()])

@app.route ("/api/v1/scripts/<name>", methods=["POST"])
def post_scripts (name):
    global SCRIPTS
    if not name in SCRIPTS:
        make_jresponse ({
            "error" : "Script name '{name}' not found"},
            http.HTTPStatus.NOT_FOUND)

    resume_bytes = request.get_data ()
    assert resume_bytes

    #TODO: put some boundaries in place
    ## What can go wrong?
    # https://pypi.org/project/defusedxml/#id24
    resume_xml = ET.fromstring (resume_bytes)
    assert resume_xml

    #TODO: make async - pust it to worker queue
    import pdb; pdb.set_trace ()
    js, code = do_jobbed (resume_xml, SCRIPTS [name]["code"])
    return make_jresponse (
        js,
        code)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
