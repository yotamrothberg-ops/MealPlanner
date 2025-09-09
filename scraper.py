import random
from logging import exception
import unicodedata
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import mealieapi
import json

MEALIE_API_KEY_FILE   = "txt files/mealie_api_token"
UNIT_MEASUREMENT_FILE = "txt files/UnitsOfMeasurements"
URL                   = "https://www.loveandlemons.com/vegetarian-recipes"
MEALIE_BASE_URL       = "http://localhost:9000/api"
DOMAIN                = "loveandlemons.com"
USERNAME              = "admin@example1.com"
PASSWORD              = "SuperSecret123"
recipe_urls           = []

with open(UNIT_MEASUREMENT_FILE, "r") as file:
    units_of_measurement = file.read().strip()
    units_of_measurement = units_of_measurement.split("\n")
    for i, unit in enumerate(units_of_measurement):
        if "/" in unit:
            units_of_measurement.append(unit.split("/")[1])
            units_of_measurement[i] = unit.split("/")[0]
    print(units_of_measurement)

with open(MEALIE_API_KEY_FILE, "r") as file:
    default_header = {
        "Authorization": f"Bearer {file.read().strip()}",
        "Content-Type": "application/json"
    }

def signup_mealie():
    login_payload = {
        "group":           "meal_planner",
        "household":       "family",
        "email":           USERNAME,
        "username":        USERNAME,
        "fullName":        "yotam rothberg",
        "password":        PASSWORD,
        "passwordConfirm": PASSWORD,
        "advanced":        False,
        "private":         False,
        "seedData":        False,
        "locale":          "en-US"

    }
    login_resp = requests.post(f"{MEALIE_BASE_URL}/api/users/register", json=login_payload)
    try:
        print(login_resp.status_code, login_resp.json())
    except Exception as e:
        print(login_resp)
        print(e)


def login_mealie():
    login_payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    login_resp = requests.post(f"{MEALIE_BASE_URL}/api/auth/oauth", json=login_payload)
    try:
        print(login_resp.status_code, login_resp.json())
    except Exception as e:
        print(login_resp)
        print(e)

def scrap_recipes_from_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    recipes = []
    for link in links:
        href = link.get('href')
        if not href: continue
        if is_internal(href): recipes.append(href)
    return recipes


def is_internal(href, domain=DOMAIN):
    parsed = urlparse(href)
    return parsed.netloc.endswith(domain)

def register_recipe_with_mealie(recipe_url):
    title = recipe_url.split("/")[-2]
    body = {
        f"actionType": "link",
        "title": title,
        "url": recipe_url
    }
    response = requests.post(f"{MEALIE_BASE_URL}/recipes/create/url", json=body, headers=default_header)
    try:
        print(response.status_code, response.json())
    except Exception as e:
        print(response)
        print(e)


def get_recipe_details(recipe_id):
    spec_recipe_url = f"{MEALIE_BASE_URL}/recipes/{recipe_id}"
    response = requests.get(spec_recipe_url, headers=default_header)
    response.raise_for_status()
    return response.json()


def get_all_recipes():
    recipe_url = f"{MEALIE_BASE_URL}/recipes"
    response = requests.get(recipe_url, headers=default_header)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    recipes = get_all_recipes()
    recipe_map = {}
    # print(f"Found {len(recipes['items'])} recipes")
    # Step 2: Loop through and fetch details
    with (open('txt files/recipes', 'a', encoding ='utf-8') as recipe_file):
        for recipe in recipes['items']:
            details = get_recipe_details(recipe["id"])
            print("---", details["name"], "---")
            recipe_map[details["name"]] = {'ingredients': [], 'id': recipe["id"]}

            for ing in details.get("recipeIngredient", []):
                food = (ing.get("food") or ing.get("note") or "").split(",")[0]
                if " or " in food: food = food.split(" or ")[random.randint(0, 1)].strip()
                recipe_map[details["name"]]['ingredients'].append(food)

        json.dump(recipe_map, recipe_file, indent=4)
