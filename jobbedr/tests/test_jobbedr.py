import pytest
from flask import url_for

def test_get_slash (client):
    response = client.get (url_for ("scripts.get_slash"))
    assert response.status_code == 200

def test_rq2 (app, client):
    with open ("../examples/resume.xml", "rt") as fp:
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
    assert job_js ["status"] == "queued" \
        or job_js ["status"] == "finished"
    assert url_for ("scripts.get_job", job_id=job_js ["id"])

    import time
    time.sleep (0.5)
    response = client.get (url_for ("scripts.get_jobs"))
    assert response.status_code == 200
    jobs_js = response.get_json ()
    found=False
    for _, urls in jobs_js.items ():
        if url_for ("scripts.get_job", job_id=job_js ["id"]) in urls:
            found = True
            break
    assert found
    
    response = client.get (url_for ("scripts.get_job", job_id=job_js ["id"]))
    assert response.status_code == 200
    job_js2 = response.get_json ()
    assert job_js2["result"]
