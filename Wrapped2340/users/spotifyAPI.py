import urllib
import base64
import requests
import os
from cryptography.x509 import random_serial_number
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

client_id = os.getenv('clientid')
redirect_uri = os.getenv('redirecturi')
scope = 'user-top-read'
state = random_serial_number()

def auth():
    base_url = 'https://accounts.spotify.com/authorize?'
    print(state)
    payload = {
        'client_id': client_id,
        'response_type': 'code',  # Authorization Code Flow
        'redirect_uri': redirect_uri,
        'scope': scope,
    }
    # Construct the authorization URL
    return base_url + urllib.parse.urlencode(payload)

def get_access_token(authorization_code):
    # Sends in the auth code to get access token and refresh token
    token_url = 'https://accounts.spotify.com/api/token'
    client_credentials = f"{os.getenv('clientid')}:{os.getenv('clientsecret')}"
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': os.getenv('redirecturi'),
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(client_credentials.encode()).decode()
    }
    response = requests.post(token_url, data=data, headers=headers)

    return response.json()
