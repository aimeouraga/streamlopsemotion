import pytest

from test import client 

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up and running"}