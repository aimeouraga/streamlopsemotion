import pytest
from tests.test import client, create_access_token, USER_NAME, SECRET_KEY, ALGORITHM



def test_predict_unsupported_file():
    # Create access token for the test user
    token = create_access_token(data={"sub": USER_NAME}, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    
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
