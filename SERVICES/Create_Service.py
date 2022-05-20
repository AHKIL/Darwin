import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import google.oauth2.credentials
import streamlit as st

def Create_Service(db, email, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = 'credentials.json'
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    cred = None

    setup_config  = db.collection('Users').document(email).collection('Google Services Token').document(API_SERVICE_NAME).get().to_dict()
    if setup_config:
        cred = setup_config
        cred = google.oauth2.credentials.Credentials.from_authorized_user_info(cred)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()
        db.collection('Users').document(email).collection('Google Services Token').document(API_SERVICE_NAME).set(json.loads(cred.to_json()))

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        return service
    except Exception as e:
        st.write(e)
        db.collection('Users').document(email).collection('Google Services Token').remove(API_SERVICE_NAME)
        return None