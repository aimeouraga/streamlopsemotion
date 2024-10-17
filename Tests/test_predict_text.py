import pytest
from tests.test import client, create_access_token, USER_NAME, SECRET_KEY, ALGORITHM



def test_predict_text():
    # Create access token for the test user
    token = create_access_token(data={"sub": USER_NAME}, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.post(
        "/predict/",
        data={"text": "I am so happy!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "predictions" in response.json()