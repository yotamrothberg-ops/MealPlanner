import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

URL = "https://www.loveandlemons.com/vegetarian-recipes"
DOMAIN = "loveandlemons.com"
recipe_urls = []

def scrap_recipes_from_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if not href: continue
        if is_internal(href): print(href)


def is_internal(url, domain=DOMAIN):
    parsed = urlparse(url)
    return parsed.netloc.endswith(domain)

if __name__ == '__main__':
    scrap_recipes_from_site(URL)

