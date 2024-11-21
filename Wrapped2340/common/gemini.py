import google.generativeai as genai
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

genai.configure(api_key=os.getenv('AI_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

def get_top_artists_locations(content):
    request = ("Can you give me list in json format of these artists countries of origin? It should be the top 5 entries, no repeats. Only the countries should be in the json. "
               "Ignore unknown countries. Do not add anything else.").join([str(item) for item in content])
    response = model.generate_content(request,
                                      generation_config=genai.types.GenerationConfig(
                                          temperature=0,
                                      )).text
    remove_list = ["`", "json", "[", "]", '"', "\n",]

    # Loop through each item and replace it in the string
    for item in remove_list:
        response = response.replace(item, "")

    response = response.strip()
    response = response.split(",")
    response = [item.strip() for item in response]
    country_array = [{"country": country} for country in response]
    print(country_array)
    return country_array

def place_to_visit(content) :
    request = ("Given these songs, where should I visit? Give me the one interesting place, landmark, or city and country. Make a outlandish, funny, rarely known place."
               "Do not add anything else.").join([str(item) for item in content])
    response = model.generate_content(request,
                                      generation_config=genai.types.GenerationConfig(
                                          temperature=1.5,
                                      )).text
    remove_list = ["`", "json", "[", "]", '"', "\n",]

    # Loop through each item and replace it in the string
    for item in remove_list:
        response = response.replace(item, "")

    return response