import urllib
import base64

import requests
import os
import secrets

from django.db.models.expressions import result
from dotenv import load_dotenv

from .models import PreviewUrl
from ..common import gemini

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
    client_credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode(client_credentials.encode()).decode()
    }
    response = requests.post(token_url, data=data, headers=headers).json()
    save_tokens(userprofile, response.get('access_token'), response.get('refresh_token'))


def get_api_data(userprofile, subdomain, time_range, limit):
    url = f'https://api.spotify.com/v1/me/top/{subdomain}'
    params = {'time_range': time_range, 'limit': limit}
    headers = {
        'Authorization': f'Bearer {userprofile.access_token}',
    }

    def api_get():
        return requests.get(url, params=params, headers=headers)

    response = api_get()

    if response.status_code == 401:  # Unauthorized, refresh token
        refresh_access_token(userprofile, userprofile.refresh_token)
        headers['Authorization'] = f'Bearer {userprofile.access_token}'
        response = api_get()

    try:
        return response.json()
    except ValueError:
        print(f"Invalid JSON response: {response.text}")
        return {"error": "Invalid response from Spotify API"}


def refresh_access_token(userprofile, refresh_token):
    client_credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
    }
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(client_credentials.encode()).decode(),
    }
    response = requests.post(token_url, data=data, headers=headers)

    try:
        response_data = response.json()
    except ValueError:
        print(f"Invalid JSON while refreshing token: {response.text}")
        return

    if "access_token" in response_data:
        save_tokens(userprofile, response_data.get('access_token'), None)
    else:
        print(f"Token refresh failed: {response_data}")


def save_tokens(userprofile, access_token, refresh_token):
    if access_token:
        userprofile.access_token = access_token
    if refresh_token:
        userprofile.refresh_token = refresh_token
    userprofile.save()
    print("saved tokens")


def get_top_artists(userprofile, limit, timeframe):
    valid_timeframes = ['short_term', 'medium_term', 'long_term']
    if timeframe not in valid_timeframes:
        print(f"Invalid time range: {timeframe}, defaulting to 'short_term'.")
        timeframe = 'short_term'  # Default to 'short_term' if invalid

    artist_response = get_api_data(
        userprofile=userprofile,
        subdomain='artists',
        time_range=timeframe,
        limit=limit,
    )
    return [{"name": artist["name"], "id": artist["id"], "genres": artist["genres"], "images": artist["images"][0]} for artist in artist_response['items']]


def get_top_tracks(userprofile, timeframe):
    tracks_response = get_api_data(
        userprofile=userprofile,
        subdomain='tracks',
        time_range=timeframe,
        limit=10
    )
    return [{"name": track["name"], "artistName": track["artists"][0]["name"], "id": track["id"], "images": track["album"]["images"][0]} for track in tracks_response['items']]


def get_wrapped_content(userprofile, timeframe):
    try:
        top_artists = get_top_artists(userprofile, 10, timeframe)
        top_50_artists = get_top_artists(userprofile, 50, timeframe)
        top_artists_locations = gemini.get_top_artists_locations(top_50_artists)
        top_tracks = get_top_tracks(userprofile, timeframe)
        preview_urls = []
        for track in top_tracks:
            # Check if the track already exists in the database
            existing_preview_url = PreviewUrl.objects.filter(name=track['name'], artist=track['artistName']).first()
            if existing_preview_url:
                # If the track exists, append the preview URL from the model
                preview_urls.append(existing_preview_url.url)
            else:
                # If the track doesn't exist, get the preview URL
                preview_url = get_preview(track['name'], track['artistName'])

                # If a preview URL was found, create a new PreviewUrl object
                if preview_url:
                    new_preview = PreviewUrl(name=track['name'], artist=track['artistName'], url=preview_url)
                    new_preview.save()
                    preview_urls.append(preview_url)

        vacation_spot = gemini.place_to_visit(top_artists)
        top_genres = get_top_genres(top_50_artists)
        combined = {
            'artists': top_artists,
            'tracks': top_tracks,
            'locations': top_artists_locations,
            "preview_urls": preview_urls,
            'vacation': vacation_spot,
            'timeframe': timeframe,
            'genres': top_genres,
        }
        return combined
    except Exception as e:
        print(f"Error fetching wrapped content: {e}")
        return {"error": "Failed to fetch wrapped content"}


def get_preview(song, artist):
    song = song.replace(' ', '+')
    params = {
        'term': song,
        'media': 'music',
        'entity': 'song',
        'limit': 5
    }
    response = requests.get('https://itunes.apple.com/search?',
                            params=params)

    results = response.json()['results']

    for track in results:
        # Check if the artist name matches
        if track['artistName'].lower() == artist.lower():  # Case insensitive comparison
            preview_url = track.get('previewUrl')
            if preview_url:
                print(track["trackName"])
                return preview_url

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


def get_top_artist_tracks(artist_id, userprofile):
    params = {
        'market': 'US'
    }
    headers = {
        'Authorization': 'Bearer %s' % userprofile.access_token,
    }
    response = requests.get('https://api.spotify.com/v1/artists/%s/top-tracks' % artist_id,
                            params=params, headers=headers)
    return response.json()['tracks']


def get_top_genres(artists):
    genre_list = []
    genre_count = {}

    # Extract genres for each artist and add to genre_list
    for artist in artists:
        genre_list.extend(artist.get("genres", []))  # Use .get to safely access genres

    # Count occurrences of each genre
    for genre in genre_list:
        if genre in genre_count:
            genre_count[genre] += 1
        else:
            genre_count[genre] = 1

    # Sort genres by count in descending order
    sorted_genres_by_count = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    # Return the sorted genres as a list of dictionaries
    return [{'genre': genre, 'count': count} for genre, count in sorted_genres_by_count]

