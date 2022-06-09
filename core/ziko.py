from typing import List

import fake_useragent
import requests
from art import tprint
from bs4 import BeautifulSoup
from rich.console import Console

from utils import save_json

# URL_API = 'https://www.ziko.pl/wp-admin/admin-ajax.php?action=get_pharmacies'
URL_POINT = 'https://www.ziko.pl/lokalizator/'
URL = 'https://www.ziko.pl/'
console = Console()


def get_soup(url: str) -> BeautifulSoup:
	"""Получаю DOM-дерево и создаю экземпляр класса bs4"""

	def get_html(url_: str) -> BeautifulSoup:
		headers = {'User-Agent': fake_useragent.UserAgent().random}
		result = requests.get(url_, headers=headers)
		if result.status_code == 200:
			return cook_soup(result.text)
		raise Exception(f'Connection error {result.status_code}')

	def cook_soup(dom: str) -> BeautifulSoup:
		return BeautifulSoup(dom, 'lxml')

	return get_html(url)


@save_json('ziko')
def get_content(soup: BeautifulSoup) -> List:
	"""Пробегаюсь по дереву и записываю list(dict)"""
	output = []
	rows = soup.find('table').find('tbody').find_all('tr')
	amount = len(rows)
	count = 0

	for row in rows:

		name = row.find('td', class_='mp-table-dermo').text.split()[:2]
		name = ' '.join(name)

		address_ = ' '.join(row.find('td', class_='mp-table-address').text.split())
		address = address_[:address_.find('tel.')].strip()
		phones = address_[address_.find('tel.') + 5:address_.find('Infolinia:')]

		items = row.find('td', class_='mp-table-hours').find_all('span')
		working_hours = []
		for num in range(0, len(items) - 1, 2):
			if items[num].text.strip().startswith('nie'):
				working_hours.append(f'nie' + items[num + 1].text)
				break
			elif items[num].text.strip().startswith('sob'):
				working_hours.append(f'sob' + items[num + 1].text)
			else:
				working_hours.append(f'{items[num].text}{items[num + 1].text}')

		raw_link = row.find('div', class_='morepharmacy').find('a').get('href')
		detail = get_soup(URL + raw_link)
		raw_geo = detail.find('div', 'coordinates').find_all('span')
		latlon = [i.text.split()[-1] for i in raw_geo]
		output.append({
			'address': address,
			'latlon': latlon,
			'name': name,
			'phones': phones,
			'working_hours': working_hours
		})
		count += 1
		console.print(f'[bold yellow][+][Ziko] Прогресс [{count}/{amount}][/bold yellow]')
	return output


def main(url: str) -> None:
	tprint('Ziko', font='cybermedium')
	console.print("[bold cyan][+][Ziko] Начинаю парсить...[/bold cyan]")
	soup = get_soup(url)
	data = get_content(soup)
	console.print(f'[bold cyan][?][Ziko] Всего объектов записано: [/bold cyan][sky underline]{len(data)}[/sky underline]')
	console.print("[bold green][+][Ziko] Парсинг окончен![/bold green]\n")


if __name__ == '__main__':
	main(URL_POINT)
