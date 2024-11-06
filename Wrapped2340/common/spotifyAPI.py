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

def get_access_token(userprofile, authorization_code):
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
    save_tokens(userprofile, response.get('access_token'), response.get('refresh_token'))

def get_api_data(userprofile, subdomain, time_range, limit):
    url = 'https://api.spotify.com/v1/me/top/%s' % subdomain
    params = {
        'time_range': time_range,
        'limit': limit,
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer %s' % userprofile.access_token,
    }
    api_get = lambda: requests.get(url, params=params, headers=headers)
    response = api_get()

    if response.status_code == 401:
        refresh_token = userprofile.refresh_token
        refresh_access_token(userprofile, refresh_token)

        headers['Authorization'] = 'Bearer %s' % userprofile.access_token
        response = api_get()

        return response.json()

    return response.json()

def refresh_access_token(userprofile, refresh_token):
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
    save_tokens(userprofile, response.get('access_token'),None)

def save_tokens(userprofile, access_token, refresh_token):
    if access_token:
        userprofile.access_token = access_token
    if refresh_token:
        userprofile.refresh_token = refresh_token
    userprofile.save()
    print("saved tokens")

def get_top_artists(userprofile, limit=10):
    artist_response = get_api_data(
        userprofile=userprofile,
        subdomain='artists',
        time_range='medium_term',
        limit=limit
    )
    return artist_response['items']

def get_top_tracks(userprofile):
    tracks_response = get_api_data(
        userprofile=userprofile,
        subdomain='tracks',
        time_range='medium_term',
        limit=10
    )
    return tracks_response['items']

def get_default_wrapped_content(userprofile):
    combined = {
        'artists': get_top_artists(userprofile),
        'tracks': get_top_tracks(userprofile)
    }
    return combined

def get_related_artists(artist_id, userprofile):
    headers = {
        'Authorization': 'Bearer %s' % userprofile.access_token,
    }
    response = requests.get('https://api.spotify.com/v1/artists/%s/related-artists' % artist_id,
                            headers=headers)
    return response.json()['artists']

def get_albums(artist_id, userprofile):
    params = {
        'include-groups': ['album', 'single'],
    }
    headers = {
        'Authorization': 'Bearer %s' % userprofile.access_token,
    }
    response = requests.get('https://api.spotify.com/v1/artists/%s/albums' % artist_id,
                            params=params, headers=headers)
    return response.json()['items']
