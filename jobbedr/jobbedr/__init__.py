import os
import http # and now we REQUIRE python3

from flask import Flask
from flask import make_response
from flask import jsonify
from flask_rq2 import RQ

# global objects
rq = RQ ()

# Flask application Factory
# used to
# 1. make application 
def create_app (
    RQ_REDIS_URL="redis://localhost:6391/0",
    ):

    app = Flask (__name__)

    #FIXME: redis workers should get their own setup
    cwd = os.getcwd ()
    # populate config for RQ2 queue
    app.config.update ((dict (
        RQ_REDIS_URL=RQ_REDIS_URL,
        CWD=cwd
    )))

    # init rq queue
    rq.init_app (app)

    # load application blueprints
    from .scripts import scripts
    app.register_blueprint (scripts)

    return app

# TODO: utils?
def make_jresponse (obj, return_code=http.HTTPStatus.OK):
    return make_response (jsonify (obj), return_code)
