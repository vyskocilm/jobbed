import pytest
from flask import url_for

def test_get_slash (client):
    response = client.get (url_for ("scripts.get_slash"))
    assert response.status_code == 200

def test_rq2 (app, client):
    with open ('../examples/resume.xml', 'br') as fp:
        data=fp.read ()
    response = client.post (
        url_for ("scripts.post_scripts", name="jobbed_html"),
        content_type="application/xml; charset=utf-8",
        data=data)
    assert response.status_code == 200

    job_js = response.get_json ()
    assert job_js ["id"]
    assert job_js ["api"]
    assert job_js ["enqueued_at"]
    assert job_js ["status"] == "queued"
    assert url_for ("scripts.get_job", job_id=job_js ["id"])

    response = client.get (url_for ("scripts.get_jobs"))
    assert response.status_code == 200
    jobs_js = response.get_json ()
    assert url_for ("scripts.get_job", job_id=job_js ["id"]) in jobs_js
