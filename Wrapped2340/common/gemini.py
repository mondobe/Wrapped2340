import google.generativeai as genai
import os
from dotenv import load_dotenv

# Loads variables from .env
load_dotenv()

genai.configure(api_key=os.getenv('AI_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash")

def get_top_artists_locations(content):
    request = ("Can you give me list in json format of these artists countries of origin? It has to be the top 5 entries, no repeats. Only the countries should be in the json. "
               "Ignore unknown countries. Do not add anything else.").join([str(item) for item in content])
    response = model.generate_content(request,
                                      generation_config=genai.types.GenerationConfig(
                                          temperature=0,
                                          top_p=0.5,
                                      )).text
    remove_list = ["`", "json", "[", "]", '"', "\n",]

    # Loop through each item and replace it in the string
    for item in remove_list:
        response = response.replace(item, "")

    response = response.strip()
    response = response.split(",")
    response = [item.strip() for item in response]
    country_array = [{"country": country} for country in response]
    #print(country_array)
    return country_array

def place_to_visit(content) :
    prompt = "Based on these songs, recommend a single unusual or rarely known place I should visit—either a landmark or a city and country. Ensure the suggestion is random and not a common choice. Include only the name and location. Avoid providing any additional information."
    request = prompt.join([str(item) for item in content])
    response = model.generate_content(request,
                                      generation_config=genai.types.GenerationConfig(
                                          temperature=1.7,
                                          top_k=5,
                                          top_p=1,
                                      )).text
    remove_list = ["`", "json", "[", "]", '"', "\n",]

    # Loop through each item and replace it in the string
    for item in remove_list:
        response = response.replace(item, "")

    return response