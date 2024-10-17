import pytest
from fastapi.testclient import TestClient
from app import app  
from datetime import datetime, timedelta
from jose import jwt
import os

client = TestClient(app)

ADMIN_NAME = os.getenv("ADMIN_NAME")
PASSWORD_ADMIN = os.getenv("PASSWORD_ADMIN")
USER_NAME = os.getenv("USER_NAME")
PASSWORD_USER = os.getenv("PASSWORD_USER")

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
APP_INSIGHTS_KEY = os.getenv("AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # `expire` is now a datetime object
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Convert the `datetime` object to a timestamp
    to_encode.update({"exp": expire.timestamp()})  # Call timestamp() on the datetime object
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt