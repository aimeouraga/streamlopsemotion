from datetime import datetime, timedelta, timezone
from typing import Union, Optional
# from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form # type: ignore
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # type: ignore
from passlib.context import CryptContext # type: ignore
import jwt # type: ignore
from jwt import PyJWTError # type: ignore
from pydantic import BaseModel # type: ignore
from transformers import pipeline # type: ignore
import fitz   # type: ignore
import pandas as pd  # type: ignore
# from dotenv import load_dotenv # type: ignore
import os
# load_dotenv()

# adminame = os.getenv('adminame')
# passwordadmin = os.getenv('passwordadmin')
# username = os.getenv('username')
# passworduser = os.getenv('passworduser')

# JWT settings
SECRET_KEY = "04f814f991c7117927ff18ebed47202093f0fea811324d2cee30d78df8a9cb88" # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User database
users_db = {
    "admin": {"username": "admin", "password": pwd_context.hash("adminpass"), "role": "admin"},
    "user": {"username": "user", "password": pwd_context.hash("userpass"), "role": "user"},
}


# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        return username
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

# Load the text-classification model
classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)

# Function that extract text from PDF
def extract_text_from_pdf(file: UploadFile) -> str:
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# Function that extract text from TXT file
def extract_text_from_txt(file: UploadFile) -> str:
    text = file.file.read().decode("utf-8")
    return text

# Function that extract text from CSV file (assume text is in a single column)
def extract_text_from_csv(file: UploadFile) -> str:
    df = pd.read_csv(file.file)
    # Assuming the text is in the first column, concatenate all rows
    text = " ".join(df.iloc[:, 0].astype(str).tolist())
    return text

@app.get("/")
def read_root():
    return {"message": "Welcome to the Emotion detection API"}

@app.post("/predict/")
async def predict(
    text: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None),
    token: str = Depends(oauth2_scheme)
):
    input_text = None

    if text:
        # If text is provided, use it
        input_text = text
    elif file:
        # Check file type and extract text
        if file.filename.endswith(".pdf"):
            input_text = extract_text_from_pdf(file)
        elif file.filename.endswith(".txt"):
            input_text = extract_text_from_txt(file)
        elif file.filename.endswith(".csv"):
            input_text = extract_text_from_csv(file)
        else:
            return {"error": "Unsupported file type. Please upload a PDF, TXT, or CSV file."}
    else:
        return {"error": "Please provide a text or upload a file for prediction"}

    # Emotions prediction
    predictions = classifier(input_text)

    return {"predictions": predictions}

@app.get("/health")
def health():
    return {"status": "up and running"}

