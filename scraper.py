from logging import exception

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import mealieapi

MEALIE_API_KEY_FILE = "mealie_api_token"
URL                 = "https://www.loveandlemons.com/vegetarian-recipes"
MEALIE_BASE_URL     = "http://localhost:9000/api"
DOMAIN              = "loveandlemons.com"
USERNAME            = "admin@example1.com"
PASSWORD            = "SuperSecret123"
recipe_urls         = []

with open(MEALIE_API_KEY_FILE, "r") as file:
    default_header = {
        "Authorization": f"Bearer {file.read().strip()}",
        "Content-Type": "application/json"
    }

def signup_mealie():
    login_payload = {
        "group": "meal_planner",
        "household": "family",
        "email": USERNAME,
        "username": USERNAME,
        "fullName": "yotam rothberg",
        "password": PASSWORD,
        "passwordConfirm": PASSWORD,
        "advanced": False,
        "private": False,
        "seedData": False,
        "locale": "en-US"

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
    print(f"Found {len(recipes['items'])} recipes")
    # Step 2: Loop through and fetch details
    for recipe in recipes['items']:
        details = get_recipe_details(recipe["id"])
        print("\n---", details["name"], "---")
        for ing in details.get("recipeIngredient", []):
            qty = ing.get("quantity") or ""
            unit = ing.get("unit") or ""
            food = ing.get("food") or ing.get("note") or ""
            print(f"- {qty} {unit} {food}")

