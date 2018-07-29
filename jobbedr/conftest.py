import pytest
import shutil
import glob
import subprocess
import itertools
import os
import time
from jobbedr import create_app

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

    _app = create_app ()
    # TODO: use flask json client to enhance testing capabilities
    #from flask_jsontools import FlaskJsonClient
    #_app.test_client_class = FlaskJsonClient
    # TODO: update co
    # update configuration somehow
    #foo = os.environ.get ("JOBBEDR_FOO")
    #_app.config.update (dict (FOO=foo))
    _app.config.update (dict (
        RQ_REDIS_URL = "redis://127.0.0.1:5001/0"))
    yield _app

    redis_server.terminate ()
    redis_server.wait (timeout=5)
    redis_server.kill ()
