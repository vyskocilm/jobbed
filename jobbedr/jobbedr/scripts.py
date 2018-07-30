import http # and now we REQUIRE python3

import tempfile
import os
from functools import partial as FP
import uuid
import subprocess
import shlex
import shutil
import defusedxml.ElementTree as ET

from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import url_for
from flask import request

from . import rq
from . import make_jresponse

scripts = Blueprint ("scripts", __name__)

def call_gsl (script, output_name, datadir=None):
    assert datadir
    subprocess.check_call (["gsl", f"-script:{datadir}/{script}.gsl", "resume.xml"])
    assert os.path.exists (output_name)
    return output_name

def call_pdflatex (output_name, datadir=None):
    cwd = os.getcwd ()
    cmd = f"docker run -w /data -v {cwd}:/data -it --rm hiono/texlive pdflatex resume.tex"
    subprocess.check_call (
        shlex.split (cmd))
    assert os.path.exists (output_name)
    return output_name

# main business logic code
def do_jobbed (workdir, datadir, staticdir, xml, resume_str, code):
    #TODO: add an extra validation of loaded XML
    #TODO: this MUST be isolated from main server
    tempdir = tempfile.TemporaryDirectory (
        prefix="jobbed",
        dir=workdir)

    cwd = os.getcwd ()
    os.chdir (tempdir.name)
    
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

    #FIXME: redis job already have uuid - can't we just get it here?
    _uuid = str (uuid.uuid4 ())
    os.makedirs (
        os.path.join (
            staticdir,
            _uuid))

    if not isinstance (code, tuple):
        code = (code, )

    outputs = []
    #FIXME: error handling
    for f in code:
        out = f (datadir=datadir)
        shutil.copy2 (out,
            os.path.join (
                staticdir,
                _uuid,
                out))
        outputs.append (f"{_uuid}/{out}")

    os.chdir (cwd)
    tempdir.cleanup ()

    return outputs, http.HTTPStatus.OK

@rq.job
def do_jobbed_rq2 (workdir, datadir, staticdir, xml, resume_str, code):
    #from flask import current_app as app
    #with app.app_context ():
    return do_jobbed (workdir, datadir, staticdir, xml, resume_str, code)

# FIXME: move out
@scripts.route('/')
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

#FIXME: register for whole app in __init__.py
@scripts.errorhandler(404)
def not_found(error):
    return make_response(
        jsonify({"error": "Not found"}),
        http.HTTPStatus.NOT_FOUND)


# List of scripts
SCRIPTS = {
    "jobbed_html" : {
        "path" : "jobbed_html.gsl",
        "description" : "Create plain html5 output",
        "code" : (FP (call_gsl, "jobbed_html", "resume.html"), )
    },
    "jobbed_latex" : {
        "path" : "jobbed_latex.gsl",
        "description" : "Create LaTeX and PDF output",
        "code" : (FP (call_gsl, "jobbed_latex", "resume.tex"),
                  FP (call_pdflatex, "resume.pdf"))
    },
}

@scripts.route ("/api/v1/scripts", methods=["GET"])
def get_scripts ():
    return make_jresponse ([
        {
            "id" : name,
            "api" : url_for (".post_scripts", name=name),
            "description": script["description"],
        }
        for name, script in SCRIPTS.items ()])

@scripts.route ("/api/v1/scripts/<name>", methods=["POST"])
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

    from flask import current_app as app
    workdir = app.config ["WORKDIR"]
    datadir = app.config ["DATADIR"]
    staticdir = app.config ["STATICDIR"]
    dq = rq.get_queue ("default")
    job = do_jobbed_rq2.queue (
        workdir,
        datadir,
        staticdir,
        resume_xml,
        resume_str,
        SCRIPTS [name]["code"],
        queue="default",
        timeout=60,
        ttl=500
        )

    #import pdb; pdb.set_trace ()
    #fq = rq.get_failed_queue ()
    #job1 = fq.jobs[0]
    #print (job1.exc_info)

    return make_jresponse ({
        "api" : url_for (".get_job", job_id=job.id),
        "id" : job.id,
        "enqueued_at" : job.enqueued_at.isoformat(),
        "status": job.status},
        200)

@scripts.route ("/api/v1/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    dq = rq.get_queue ("default")
    job = dq.fetch_job (job_id)
    if job is None:
        return make_jresponse ({
            "error": f"job id {job_id} not found"},
            http.HTTPStatus.NOT_FOUND)

    return make_jresponse ({
        "api" : url_for (".get_job", job_id=job.id),
        "id" : job.id,
        "enqueued_at" : job.enqueued_at.isoformat(),
        "status": job.status},
        200)

@scripts.route ("/api/v1/jobs/", methods=["GET"])
def get_jobs ():
    dq = rq.get_queue ("default")
    return make_jresponse (
        [url_for (".get_job", job_id=_id) for _id in dq.get_job_ids ()],
        200)

if __name__ == "__main__":
    app = create_app ()
    app.run ()
