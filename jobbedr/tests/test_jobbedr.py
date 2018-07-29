import pytest
from flask import url_for

def test_app (client):
    response = client.get (url_for ("scripts.get_slash"))
    assert response.status_code == 200

def _test_jobbed_rq2 (app, client):
    import pdb; pdb.set_trace ()
    with open ('../examples/resume.xml', 'br') as fp:
        data=fp.read ()
    response = client.post (
        url_for ("post_scripts", name="jobbed_html"),
        content_type="application/xml; charset=utf-8",
        data=data)
    assert response.status_code == 200
