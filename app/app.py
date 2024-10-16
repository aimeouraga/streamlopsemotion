from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.auth import Token, authenticate_user, User, get_current_active_user, create_access_token
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from pydantic import BaseModel
from transformers import pipeline
import fitz
import pandas as pd
from dotenv import load_dotenv
import os
import logging
from azure.storage.blob import BlobServiceClient
from opencensus.ext.azure.log_exporter import AzureLogHandler
import time
import io

load_dotenv()

ADMIN_NAME = os.getenv("ADMIN_NAME")
PASSWORD_ADMIN = os.getenv("PASSWORD_ADMIN")
USER_NAME = os.getenv("USER_NAME")
PASSWORD_USER = os.getenv("PASSWORD_USER")

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
APP_INSIGHTS_KEY = os.getenv("AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY")

# Blob Storage setup
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_name = "project2"
container_client = blob_service_client.get_container_client(container_name)
csv_blob_name = "first_project_predict_log.csv"

# Application Insights logger setup
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string=f'InstrumentationKey={APP_INSIGHTS_KEY}'))
logger.setLevel(logging.INFO)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        data={"sub": user.username}, expires_delta=access_token_expires
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

# Loading the model
classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=1)


def extract_text_from_pdf(file: UploadFile) -> str:
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_txt(file: UploadFile) -> str:
    text = file.file.read().decode("utf-8")
    return text

def extract_text_from_csv(file: UploadFile) -> str:
    df = pd.read_csv(file.file)
    text = " ".join(df.iloc[:, 0].astype(str).tolist())
    return text

def save_predictions_to_blob(predictions_df: pd.DataFrame):
    try:
        # Download existing CSV file if it exists
        blob_client = container_client.get_blob_client(csv_blob_name)
        blob_data = None
        if blob_client.exists():
            download_stream = blob_client.download_blob()
            blob_data = download_stream.readall()
        
        if blob_data:
            existing_df = pd.read_csv(io.BytesIO(blob_data))
            predictions_df = pd.concat([existing_df, predictions_df])

        # Save the updated DataFrame back to blob storage
        output_stream = io.StringIO()
        predictions_df.to_csv(output_stream, index=False)
        blob_client.upload_blob(output_stream.getvalue(), overwrite=True)
    except Exception as e:
        logger.error(f"Error saving predictions to blob: {e}")

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

    # Decode the user token and log the request
    username = decode_token(token)
    logger.info(f"User: {username} made a prediction request.")
    
   
    request_time = datetime.now(timezone.utc)
    start_time = time.time()

    if text:
        input_text = text
    elif file:
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

    # Capture the end time and calculate response time
    response_time = time.time() - start_time
    # print(response_time)

    
    prediction_data = {
        "username": username,
        "request_time": request_time.isoformat(),
        "response_time": response_time,
        "Texts": input_text,
        "predictions": predictions[0][0].get('label', 'Unknown label'),
        "score": predictions[0][0].get('score', 'No score')
    }

    predictions_df = pd.DataFrame([prediction_data])

    save_predictions_to_blob(predictions_df)

    # Log the prediction result
    logger.info(f"Prediction: {predictions} for user: {username}")

    return {"predictions": predictions}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/health")
def health():
    return {"status": "up and running"}
