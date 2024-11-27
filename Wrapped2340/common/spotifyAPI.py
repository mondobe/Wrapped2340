import time
import urllib
import base64

import requests
import os
import secrets
from dotenv import load_dotenv
from ..common import gemini
from requests import RequestException

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
    return [{"name": artist["name"], "id": artist["id"], "genres": artist["genres"]} for artist in artist_response['items']]


def get_top_tracks(userprofile, timeframe):
    tracks_response = get_api_data(
        userprofile=userprofile,
        subdomain='tracks',
        time_range=timeframe,
        limit=10
    )
    return [{"name": track["name"], "preview_url": track["preview_url"], "id": track["id"]} for track in tracks_response['items']]


def get_wrapped_content(userprofile, timeframe):
    try:
        top_artists = get_top_artists(userprofile, 10, timeframe)
        top_artists_locations = gemini.get_top_artists_locations(top_artists)
        top_tracks = get_top_tracks(userprofile, timeframe)
        preview_urls = []
        for track in top_tracks:
            if "preview_url" in track:
                preview_urls.append({"url": track["preview_url"]})
                del track["preview_url"]  # Remove the preview_url field
        vacation_spot = gemini.place_to_visit(top_tracks)

        combined = {
            'artists': top_artists,
            'tracks': top_tracks,
            'locations': top_artists_locations,
            "preview_urls": preview_urls,
            'vacation': vacation_spot,
            'timeframe': timeframe,
            'genres': get_top_genres(userprofile, timeframe),
        }
        return combined
    except Exception as e:
        print(f"Error fetching wrapped content: {e}")
        return {"error": "Failed to fetch wrapped content"}
    


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


def get_top_genres(userprofile, timeframe, limit=50):
    artists = get_top_artists(userprofile, limit, timeframe)
    genre_count = {}

    for artist in artists:
        artist_id = artist['id']
        artist_info = get_artist_info(userprofile, artist_id)

        for genre in artist_info.get('genres', []):  # Handle empty genres list
            genre_count[genre] = genre_count.get(genre, 0) + 1

    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    return [{'genre': genre, 'count': count} for genre, count in sorted_genres]


def get_artist_info(userprofile, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {
        'Authorization': f'Bearer {userprofile.access_token}',
    }

    response = make_api_request(url, {}, headers)

    if response is None:
        raise ValueError(f"Failed to get artist info for artist ID: {artist_id}")

    return response  # Returns the artist info, including genres and images



def make_api_request(url, params, headers, max_retries=5, initial_backoff=1):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', initial_backoff))
                time.sleep(retry_after)
            elif attempt == max_retries - 1:
                raise e
            else:
                time.sleep(initial_backoff * (2 ** attempt))
    return None


def get_artist_images(top_artists):
    artists_info = []
    for artist in top_artists:
        artist_info = {
            'name': artist['name'],
            'popularity': artist.get('popularity', 0),  # Use get() with a default value
            'image_url': artist['images'][0]['url'] if artist.get('images') else None,
            'spotify_url': artist['external_urls'].get('spotify', '')
        }
        artists_info.append(artist_info)
    return artists_info


def get_song_images(top_songs):
    songs_info = []
    for song in top_songs['items']:  # Ensure you're accessing the 'items' key correctly
        print(f"Song data: {song}")  # Debugging to verify structure
        song_info = {
            'name': song['name'],
            'popularity': song['popularity'],
            'image_url': song['album']['images'][0]['url'] if song['album'].get('images') else 'default_image_url_here',  # Fallback if no image
            'spotify_url': song['external_urls']['spotify'],
            'preview_url': song['preview_url']
        }
        songs_info.append(song_info)
    return songs_info
