import os
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


def get_google_credentials():
    """Get Google API credentials with OAuth flow"""
    
    credentials_file = settings.GOOGLE_CREDENTIALS_FILE
    token_file = settings.GOOGLE_TOKEN_FILE
    
    creds = None
    
    # Check if token.json exists
    if os.path.exists(token_file):
        creds = UserCredentials.from_authorized_user_file(token_file)
    
    # If no token or token expired, perform OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_file}. "
                    "Please download it from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, settings.GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save token for next run
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds
