import os
from datetime import timedelta
from fastapi.testclient import TestClient
from app import app
from auth import create_access_token

USER_NAME = os.getenv("USER_NAME")

ACCESS_TOKEN_EXPIRE_MINUTES=30

client = TestClient(app)
# Test the root endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Emotion detection API"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "up and running"}

def test_predict_no_auth():
    response = client.post(
        "/predict/",
        data={"text": "I am so happy!"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_predict_text():
    # Create access token for the test user
    token = create_access_token(data={"sub": USER_NAME},expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    response = client.post(
        "/predict/",
        data={"text": "I am so happy!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "predictions" in response.json()

def test_predict_unsupported_file():
    # Create access token for the test user
    token = create_access_token(data={"sub": USER_NAME},expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    with open("test_file.docx", "w") as f:
        f.write("This is a test file.")
        
    with open("test_file.docx", "rb") as file:
        response = client.post(
            "/predict/",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test_file.docx", file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
    assert response.status_code == 200
    assert response.json() == {"error": "Unsupported file type. Please upload a PDF, TXT, or CSV file."}