import os
import http # and now we REQUIRE python3
import subprocess #TODO only for subprocess module
import multiprocessing
from urllib.parse import urlparse
import logging

from flask import Flask
from flask import make_response
from flask import jsonify
from flask_rq2 import RQ

from redis import StrictRedis
from rq import push_connection, get_failed_queue
from rq.handlers import move_to_failed_queue  # RQ's default exception handler

from .foo import my_handler

# global objects
rq = RQ ()
rq_workers = []

# Flask application Factory
# used to
# 1. make application 
def create_app (
    RQ_REDIS_URL="redis://localhost:6391/0",
    RQ_REDIS_WORKERS=None,
    WORKDIR=None,
    DATADIR=None,
    STATICDIR=None
    ):

    #TODO: join STATICDIR with flask app
    cwd = os.getcwd ()
    if STATICDIR is None:
        STATICDIR = os.path.join (
            cwd,
            "jobbedr",
            "static")
    assert os.path.isdir (STATICDIR)

    if WORKDIR is None:
        WORKDIR = os.path.join (
            cwd,
            "jobbedr",
            "workdir")
    assert os.path.isdir (WORKDIR)

    if DATADIR is None:
        DATADIR = os.path.join (
            cwd,
            "..")
    assert os.path.isdir (DATADIR)
    
    app = Flask (__name__)

    # populate config for RQ2 queue
    app.config.update ((dict (
        RQ_REDIS_URL=RQ_REDIS_URL,
        WORKDIR=WORKDIR,
        DATADIR=DATADIR,
        STATICDIR=STATICDIR
    )))

    # init rq queue
    rq.init_app (app)

    if RQ_REDIS_WORKERS is None:
        RQ_REDIS_WORKERS=int (subprocess.check_output ("nproc"))

    # initialize workers
    for i in range (RQ_REDIS_WORKERS):
        worker = rq.get_worker ('default')
        worker.log.setLevel (logging.DEBUG)
        proc = multiprocessing.Process (target=worker.work, kwargs={'burst': False})
        rq_workers.append (proc)
        proc.start ()

    # get an access to faled queue - this does not look like best Pythonnic API we can have ...
    # see documentation: http://python-rq.org/docs/jobs/
    # we solve it by adding new method to out rq object
    pr = urlparse (RQ_REDIS_URL)
    assert pr.scheme == "redis", "Support for protocols outside of redis:// are not implemented"
    host = pr.netloc.split (':')[0]
    port = int (pr.netloc.split (':')[1])
    db = pr.path [1:]

    con = StrictRedis(host=host, port=port, db=db)
    push_connection(con)

    rq.get_failed_queue = lambda: get_failed_queue ()

    # load application blueprints
    from .scripts import scripts
    app.register_blueprint (scripts)

    return app

# TODO: utils?
def make_jresponse (obj, return_code=http.HTTPStatus.OK):
    return make_response (jsonify (obj), return_code)
