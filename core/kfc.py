import json
from typing import List

import fake_useragent
import requests

from utils import save_json
from art import tprint
from rich.console import Console

URL_POINT = 'https://api.kfc.com/api/store/v2/store.get_restaurants?showClosed=true'


@save_json('raw_kfc')
def get_request(url: str) -> str:
	"""Получаю «сырой» JSON по API KFC"""
	headers = {'User-Agent': fake_useragent.UserAgent().random}
	result = requests.get(url, headers=headers)

	if result.status_code == 200:
		return json.loads(result.text)
	else:
		raise Exception(f'Connection error {result.status_code}')


@save_json('kfc')
def get_data(raw_data) -> List:
	"""Пробегаю по дереву JSON и забираю нужную инфу"""
	output = []

	for item in raw_data['searchResults']:

		address = item['storePublic']['contacts']['streetAddress'].get('ru', False)
		latlon = item['storePublic']['contacts']['coordinates']['geometry'].get('coordinates', False)
		name = item['storePublic']['title'].get('ru', False)

		check_work_time = item['storePublic']['openingHours']['regular'].get('startTimeLocal', False)
		if check_work_time is None:
			working_hours = ['closed']
		else:
			weekdays_from = item['storePublic']['openingHours']['regularDaily'][0]['timeFrom'][0:5]
			weekdays_to = item['storePublic']['openingHours']['regularDaily'][0]['timeTill'][0:5]
			weekends_from = item['storePublic']['openingHours']['regularDaily'][5]['timeFrom'][0:5]
			weekends_to = item['storePublic']['openingHours']['regularDaily'][5]['timeTill'][0:5]
			working_hours = [f'пн - пт {weekdays_from} до {weekdays_to}', f'сб-вс {weekends_from}-{weekends_to}']
		# Нормализую данные от тестовых значений
		validation = [address, latlon, name, working_hours]
		if all(validation) and name.startswith('KFC'):
			output.append({
				'address': address,
				'latlon': latlon,
				'name': name,
				'working_hours': working_hours
			})
	return output


def main(url: str) -> None:
	raw_data = get_request(url)
	data = get_data(raw_data)
	console.print(f'[bold cyan][?][KFC] Всего объектов: [/bold cyan][sky underline]{len(data)}[/sky underline]')


if __name__ == '__main__':
	tprint('KFC', font='cybermedium')
	console = Console()
	console.print("[bold cyan][+][KFC] Начинаю парсить...[/bold cyan]")
	main(URL_POINT)
	console.print("[bold green][+][KFC] Парсинг окончен![/bold green]\n")
