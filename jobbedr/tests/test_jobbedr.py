import pytest
from flask import url_for

def test_app (client):
    response = client.get (url_for ("get_slash"))
    assert response.status_code == 200
