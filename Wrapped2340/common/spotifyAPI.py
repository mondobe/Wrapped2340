import urllib
import base64
import requests
import os
import secrets
from Wrapped2340.users.models import UserProfile
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

client_id = os.getenv('CLIENT_ID')
redirect_uri = os.getenv('REDIRECT_URI')
scope = 'user-top-read'
state = secrets.token_urlsafe(16)
token_url = 'https://accounts.spotify.com/api/token'

def auth():
    base_url = 'https://accounts.spotify.com/authorize?'
    payload = {
        'client_id': client_id,
        'response_type': 'code',  # Authorization Code Flow
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
    }
    # Construct the authorization URL
    return base_url + urllib.parse.urlencode(payload)

def get_access_token(self, authorization_code):
    # Sends in the auth code to get access token and refresh token
    client_credentials = f"{os.getenv('client_id')}:{os.getenv('client_secret')}"
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': os.getenv('redirect_uri'),
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(client_credentials.encode()).decode()
    }
    response = requests.post(token_url, data=data, headers=headers).json()
    save_tokens(self, response.get('access_token'), response.get('refresh_token'))

def get_top_artists(self, access_token, time_range, limit):
    url = 'https://api.spotify.com/v1/me/top/artists'
    params = {
        'time_range': time_range,
        'limit': limit,
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + access_token,
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 401:
        refresh_token = UserProfile.objects.get(user=self.request.user).refresh_token
        refresh_access_token(self, refresh_token)

        headers['Authorization'] = 'Bearer ' + str(UserProfile.objects.get(user=self.request.user).access_token)
        response = requests.get(url, params=params, headers=headers)

        return response.json()

    return response.json()

def refresh_access_token(self, refresh_token):
    print('refreshed token')
    client_credentials = f"{os.getenv('client_id')}:{os.getenv('client_secret')}"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(client_credentials.encode()).decode()
    }
    response = requests.post(token_url, data=data, headers=headers).json()
    print(response)
    save_tokens(self, response.get('access_token'),None)

def save_tokens(self, access_token, refresh_token):
    user = UserProfile.objects.get(user=self.request.user)
    if access_token:
        user.access_token = access_token
    if refresh_token:
        user.refresh_token = refresh_token
    user.save()
    print("saved tokens")