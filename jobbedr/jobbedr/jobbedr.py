#!flask/bin/python

import http # and now we REQUIRE python3

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import url_for
from flask import request
import defusedxml.ElementTree as ET
import tempfile
import os
from functools import partial as FP
import uuid
import subprocess
import shlex
import shutil

app = Flask(__name__)
CWD = os.getcwd ()

def make_jresponse (obj, return_code=http.HTTPStatus.OK):
    return make_response (jsonify (obj), return_code)

def call_gsl (cwd, script, output_name):
    subprocess.check_call (["gsl", f"-script:{cwd}/../{script}.gsl", "resume.xml"])
    assert os.path.exists (output_name)
    return output_name

def call_pdflatex (output_name):
    PWD=os.getcwd ()
    cmd = f"docker run -w /data -v {PWD}:/data -it --rm hiono/texlive pdflatex resume.tex"
    subprocess.check_call (
        shlex.split (cmd))
    assert os.path.exists (output_name)
    return output_name

# main business logic code
def do_jobbed (xml, resume_str, code):
    global CWD
    #TODO: add an extra validation of loaded XML
    #TODO: this MUST be isolated from main server
    workdir = tempfile.TemporaryDirectory (
        prefix="jobbed",
        dir=os.path.join (CWD, "workdir"))

    cwd = CWD
    os.chdir (workdir.name)
    
    # FIXME: ElementTree's API is AWFULL!! Can't believe this is the best
    # API for Python. How on earth can .parse return ElementTree, where
    # .formstring (which accepts bytes**!!) returns Element???
    #
    # The problem is that you CAN'T WRITE utf-8 XML you read fromstring
    # such convoluted API is f*cking hard to use!!!!!
    #
    # Solved it by passing decoded unicode
    with open ("resume.xml", "wt") as resume_file:
        resume_file.write (resume_str)

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
        shutil.copy2 (out,
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
def get_slash():
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
        "code" : (FP (call_gsl, CWD, "jobbed_latex", "resume.tex"),
                  FP (call_pdflatex, "resume.pdf"))
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

    cl = request.content_length
    if cl > 32635:
        return make_jresponse (
            {"error": f"requested entity too large: {cl}"},
             http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE)

    global SCRIPTS
    if not name in SCRIPTS:
        make_jresponse ({
            "error" : "Script name '{name}' not found"},
            http.HTTPStatus.NOT_FOUND)

    resume_bytes = request.get_data ()
    assert resume_bytes
    #TODO: add try: catch: for bad request
    resume_str = resume_bytes.decode ('utf-8')

    #TODO: add try: catch: for bad request
    resume_xml = ET.fromstring (resume_str)
    assert resume_xml

    #TODO: make async - pust it to worker queue
    js, code = do_jobbed (resume_xml, resume_str, SCRIPTS [name]["code"])
    return make_jresponse (
        js,
        code)
