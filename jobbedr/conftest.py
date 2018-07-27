import pytest

@pytest.fixture
def app ():
    """Flask application to be used in tests"""

    from jobbedr import app as _app
    # TODO: use flask json client to enhance testing capabilities
    #from flask_jsontools import FlaskJsonClient
    #_app.test_client_class = FlaskJsonClient
    # TODO: update co
    # update configuration somehow
    #foo = os.environ.get ("JOBBEDR_FOO")
    #_app.config.update (dict (FOO=foo))
    return _app

import shutil
import glob

for d in glob.glob ("jobbedr/static/*"):
    shutil.rmtree (d)
for d in glob.glob ("jobbedr/workdir/*"):
    shutil.rmtree (d)
