import pytest
from tests.test import client


def test_predict_no_auth():
    response = client.post(
        "/predict/",
        data={"text": "I am so happy!"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}