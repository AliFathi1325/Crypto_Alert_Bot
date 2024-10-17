import requests
from bs4 import BeautifulSoup

def get_token_data(token):
    response = requests.get(f'https://coinmarketcap.com/currencies/{token}/')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('span', class_='sc-65e7f566-0 WXGwg base-text').text
        return price