import pytest
import shutil
import glob
import subprocess
import itertools
import os
import time
from jobbedr import create_app
from jobbedr import rq_workers

@pytest.fixture
def app ():
    """Flask application to be used in tests"""
    for d in itertools.chain (
        glob.glob ("jobbedr/static/*"),
        glob.glob ("jobbedr/workdir/*"),
        glob.glob (".redis*")):
        shutil.rmtree (d)
    os.mkdir (".redis")
    redis_server = subprocess.Popen ((
        "/usr/sbin/redis-server",
        "--port",
        "5001",
        "--dir",
        ".redis",
    ))

    # this is MANDATORY for workers running under Flask - do not ask me why
    os.environ ["FLASK_APP"]="jobbedr:create_app('redis://127.0.0.1:5001/0', 0)"
    #os.environ ["SERVER_NAME"]="localhost:5000"

    _app = create_app (
        RQ_REDIS_URL="redis://127.0.0.1:5001/0",
        RQ_REDIS_WORKERS=1
    )
    # TODO: use flask json client to enhance testing capabilities
    #from flask_jsontools import FlaskJsonClient
    #_app.test_client_class = FlaskJsonClient

    # mandatory for url_for external=True
    _app.config ["SERVER_NAME"]="localhost:5000"
    yield _app

    for proc in rq_workers:
        proc.terminate ()

    redis_server.terminate ()
    redis_server.wait (timeout=5)
    redis_server.kill ()
