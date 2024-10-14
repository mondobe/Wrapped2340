import requests
from django.shortcuts import render,redirect
from . import spotifyAPI
import os
from dotenv import load_dotenv

from .spotifyAPI import client_id

# Loads variables from .env
load_dotenv()

# Create your views here.
def link(request):
    if request.POST.get('action') == 'link':
        print('button clicked')
        url = spotifyAPI.auth()
        return redirect(url)

    if 'code' in request.GET:
        # Extract the code from the URL
        authorization_code = request.GET['code']

        # Grabs tokens
        response_data = spotifyAPI.get_access_token(authorization_code)

        # Gets specific data
        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')

        print(response_data)
        print(access_token)

    return render(request, "users/link.html", context=None)