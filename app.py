import streamlit as st # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
from PyPDF2 import PdfReader  # type: ignore # You might need to install PyPDF2 for PDF handling
import io

API_URL = "http://127.0.0.1:8000"
TOKEN_ENDPOINT = f"{API_URL}/token"
PREDICT_ENDPOINT = f"{API_URL}/predict/"

# Initialize session state for authorization and access token
if "authorized" not in st.session_state:
    st.session_state["authorized"] = False
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

# Sidebar: Login to get access token
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    response = requests.post(TOKEN_ENDPOINT, data={"username": username, "password": password})
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        st.sidebar.success("Logged in successfully")
        st.sidebar.text("Access Token:")
        st.sidebar.code(access_token)
        st.session_state["access_token"] = access_token
    else:
        st.sidebar.error("Login failed")

# Step 2: Authorization
st.sidebar.title("Authorization")
auth_username = st.sidebar.text_input("Enter Username Again")
auth_password = st.sidebar.text_input("Enter Password Again", type="password")
client_secret = st.sidebar.text_input("Paste Access Token", type="password")

if st.sidebar.button("Authorize"):
    access_token = st.session_state["access_token"]
    if access_token and auth_username == username and auth_password == password and client_secret == access_token:
        st.sidebar.success("Authorization successful")
        st.session_state["authorized"] = True
    else:
        st.sidebar.error("Authorization failed. Please check your credentials or token.")

# Main Page: Allow file upload only after successful authorization
if st.session_state["authorized"]:
    st.title("Emotion Detection")

    file_option = st.radio("Choose input type:", ("Text", "PDF", "TXT", "CSV"))

    if file_option == "Text":
        input_text = st.text_area("Enter text for prediction")

    elif file_option in ["PDF", "TXT", "CSV"]:
        uploaded_file = st.file_uploader(f"Upload {file_option} file")
        input_text = None

    predict_response = None

    if st.button("Predict"):
        headers = {"Authorization": f"Bearer {client_secret}"}

        if file_option == "Text" and input_text:
            # Prediction for text input
            predict_response = requests.post(
                PREDICT_ENDPOINT,
                headers=headers,
                data={"text": input_text}
            )

            if predict_response.status_code == 200:
                st.success("Prediction Result:")
                predictions = predict_response.json()['predictions'][0]

                # Create dataframe to show text, label, and score
                result_df = pd.DataFrame([{
                    "Text": input_text,
                    "Label": pred.get('label', 'Unknown label'),
                    "Score": pred.get('score', 'No score')
                } for pred in predictions])
                st.dataframe(result_df)

        elif uploaded_file:
            if file_option == "PDF":
                # Extract text from PDF file
                pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                full_text = ""
                for page in pdf_reader.pages:
                    # page = pdf_reader.getPage(page_num)
                    full_text += page.extract_text()

                # Split the text into chapters
                chapters = full_text.split("Chapter ")  # Split by chapter identifier
                
                predictions_list = []
                for chapter in chapters[1:]:  # Skip the first item as it's before "Chapter 1"
                    chapter_title = "Chapter " + chapter.split("\n")[0]  # Get chapter title
                    chapter_text = chapter[len(chapter_title):].strip()  # Get chapter content

                    # Make prediction for the entire chapter text
                    predict_response = requests.post(
                        PREDICT_ENDPOINT,
                        headers=headers,
                        data={"text": chapter_text}
                    )

                    if predict_response.status_code == 200:
                        predictions = predict_response.json()['predictions'][0]
                        for pred in predictions:
                            predictions_list.append({
                                "Text": f"{chapter_text[0:70]}...",
                                "Label": pred.get('label', 'Unknown label'),
                                "Score": pred.get('score', 'No score')
                            })

                if predictions_list:
                    st.dataframe(pd.DataFrame(predictions_list))


            elif file_option == "TXT":
                # Extract text from TXT file
                input_text = uploaded_file.read().decode("utf-8")
                paragraphs = input_text.split("\n\n")  # Split by double newline to simulate paragraphs

                predictions_list = []
                for paragraph in paragraphs:
                    predict_response = requests.post(
                        PREDICT_ENDPOINT,
                        headers=headers,
                        data={"text": paragraph}
                    )
                    if predict_response.status_code == 200:
                        predictions = predict_response.json()['predictions'][0]
                        for pred in predictions:
                            predictions_list.append({
                                "Paragraph": paragraph[:50],  # Show only first 50 characters for preview
                                "Label": pred.get('label', 'Unknown label'),
                                "Score": pred.get('score', 'No score')
                            })

                if predictions_list:
                    st.dataframe(pd.DataFrame(predictions_list))

            elif file_option == "CSV":
                # Read CSV file
                df = pd.read_csv(uploaded_file)

                predictions_list = []
                for index, row in df.iterrows():
                    row_text = ' '.join([str(item) for item in row])  # Combine row elements into a text
                    predict_response = requests.post(
                        PREDICT_ENDPOINT,
                        headers=headers,
                        data={"text": row_text}
                    )

                    if predict_response.status_code == 200:
                        predictions = predict_response.json()['predictions'][0]
                        label = predictions[0].get('label', 'Unknown label')
                        score = predictions[0].get('score', 'No score')
                        predictions_list.append({
                            "Label": label,
                            "Score": score
                        })

                # Combine original dataframe with the prediction results
                result_df = pd.concat([df, pd.DataFrame(predictions_list)], axis=1)
                st.dataframe(result_df)

else:
    st.info("Please complete login and authorization to proceed.")

