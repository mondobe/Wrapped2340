import google.generativeai as genai
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

genai.configure(api_key=os.getenv('AI_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

def get_top_artists_locations(content):
    request = "Can you give me list in json format of these artists, in order, countries of origin?" + content
    response = model.generate_content(request)
    print(response.text)
