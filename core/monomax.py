import re
from typing import List

from art import tprint
from bs4 import BeautifulSoup
from rich.console import Console

from .ziko import get_soup
from .utils import save_json

URL_POINT = 'https://monomax.by/map'
console = Console()


@save_json('monomax')
def get_content(soup: BeautifulSoup) -> List:
	output = []

	raw_geo_from_js = str(soup.find_all('script')[-1])
	latlons = re.findall(r'\d+\.\d+,\s+\d+\.\d+', raw_geo_from_js)[1:]

	shops = soup.find('div', class_='all-shops').find_all('div')
	for num, shop in enumerate(shops):
		address = shop.find('p', class_='name').text

		latlon = latlons[num].split(', ')
		latlon = list(map(float, latlon))

		phone = shop.find('p', class_='phone').find('a').text
		phone = re.sub(r'[()\s]', '', phone)

		output.append({
			'address': address,
			'latlon': latlon,
			'name': 'Мономах',
			'phones': phone
		})
	return output


def parse():
	tprint('Monomax', font='cybermedium')
	console.print("[bold][+][Monomax] Начинаю парсить...[/bold]", style='#BA2B31')
	soup = get_soup(URL_POINT)
	data = get_content(soup)
	console.print(
		f'[bold][?][Monomax] Всего объектов записано: [/bold]{len(data)}', style='#BA2B31')
	console.print("[bold][+][Monomax] Парсинг окончен![/bold]\n", style='#16C60C')


if __name__ == '__main__':
	parse()
