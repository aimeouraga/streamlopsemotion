# Emotion Detection from Text for Product Reviews

## Overview

This project, **Emotion Detection from Text for Product Reviews**, is part of the MLOps course in the **AMMI (African Master's in Machine Intelligence)** program. The goal of this project is to automatically detect emotions from customer product reviews using a pre-trained sentiment analysis model. The system helps marketing teams gain valuable insights into customer emotions, enabling them to refine their strategies and improve customer satisfaction.

## Table of Contents

- [Project Description](#project-description)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Tests](#tests)
- [Contributors](#contributors)

## Project Description

The **Emotion Detection from Text for Product Reviews** project automates the process of analyzing product reviews and predicting the associated emotion. It provides actionable insights to marketing teams, reducing manual efforts in reviewing large datasets.

### Objectives

- Classify product reviews into emotional categories.
- Provide batch and real-time emotion detection for collected product reviews.
- Deploy the solution to the cloud for scalability and real-time access.
- Offer a user-friendly interface for submitting and visualizing predictions.
- Log predictions and performance metrics for continuous monitoring and improvement.

## Key Features

- **Pre-trained Emotion Detection Model**: Leverages a pre-trained [RoBerta](https://huggingface.co/SamLowe/roberta-base-go_emotions) model fine-tuned for detecting emotions from text.
- **Batch and Real-Time Inference**: Supports both real-time predictions and batch processing for large datasets.
- **OAuth2 Authentication**: Secures API access using OAuth2 and JWT tokens.
- **Logging and Monitoring**: Logs prediction details and system metrics to Azure Blob Storage and Application Insights.
- **Cloud-Based Deployment**: Deployed on Microsoft Azure.

## Architecture Overview

### System Design
This system design follows the [Serving Template Pattern](https://github.com/mercari/ml-system-design-pattern/blob/master/Serving-patterns/Serving-template-pattern/design_en.md) for scalable emotion detection of product reviews. It structures the project into an ML Core for data pipeline and model inference, Non-ML Core for API handling, authentication, and data validation, and Infrastructure for CI/CD deployment. The architecture enables real-time and batch processing with logging, monitoring, and automated retraining, ensuring efficient handling of large volumes of product reviews.

![System Design](images/System_Design.jpg)

## Setup & Installation

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Azure account with access to Blob Storage
- Docker 

### Clone the Repository

```bash
git clone https://github.com/your-username/emotion-detection-product-reviews.git
cd emotion-detection-product-reviews
```

### Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a .env file in the root directory and configure the following:
```bash
AZURE_CONNECTION_STRING="<your_azure_blob_storage_connection_string>"
AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY="<your_app_insights_key>"
MODEL_URL="<url_to_pretrained_model_in_azure_blob>"
TOKENIZER_URL="<url_to_tokenizer_in_azure_blob>"
EMBEDDING_URL="<url_to_embedding_matrix_in_azure_blob>"
USER_NAME="<default_username>"
PASSWORD="<default_password>"
SECRET_KEY="<your_jwt_secret_key>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
``` 

### Running the Application

#### Running Locally

To run the FastAPI application locally, execute the following command:
```bash
uvicorn app.app:app --reload
``` 
#### API Endpoints
To interact with the app:
- Authentication (POST /token): Authenticate and obtain a JWT token.
- Prediction (POST /predict): Predict the sentiment of a product review.
- Health Check (GET /health): Check if the API is running and the model is loaded.


#### Docker Deployment

To build and run the application with Docker, use the following commands:
```bash
docker build -t emotion-detection-app .
docker run -p 8000:8000 emotion-detection-app
``` 

### Tests

Unit tests for the key functionalities (model loading, authentication, sentiment prediction, etc.) are located in the tests/ directory. To run the tests, execute:
```bash
pytest 
``` 


### Contributors
For any question or suggestions feel free to reach out :
- [Ahmed Abdalla](aabdalla@aimsammi.org)
- [Duaa Alshareif](dalshareif@aimsammi.org)
- [Ouraga Aime ](oballou@aimsammi.org)

