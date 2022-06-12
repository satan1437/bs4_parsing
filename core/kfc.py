import json
from typing import List

import fake_useragent
import requests
from art import tprint
from rich.console import Console

from .utils import save_json

URL_POINT = 'https://api.kfc.com/api/store/v2/store.get_restaurants?showClosed=true'
console = Console()


def get_request(url: str) -> str:
	"""Получаю «сырой» JSON по API KFC"""
	headers = {'User-Agent': fake_useragent.UserAgent().random}
	result = requests.get(url, headers=headers)

	if result.status_code == 200:
		return json.loads(result.text)
	raise Exception(f'Connection error {result.status_code}')


@save_json('kfc')
def get_data(raw_data) -> List[dict]:
	"""Пробегаю по дереву JSON и забираю нужную инфу"""
	output = []
	amount = len(raw_data['searchResults'])

	for count, item in enumerate(raw_data['searchResults']):

		address = item['storePublic']['contacts']['streetAddress'].get('ru', False)
		latlon = item['storePublic']['contacts']['coordinates']['geometry'].get('coordinates', False)
		name = item['storePublic']['title'].get('ru', False)
		phone = item['storePublic']['contacts'].get('phoneNumber', False)

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
		validation = [address, latlon, name, working_hours, phone]
		if all(validation) and name.startswith('KFC'):
			output.append({
				'address': address,
				'latlon': latlon,
				'name': name,
				'phones': phone,
				'working_hours': working_hours
			})
		console.print(f'[bold][+][KFC] Прогресс [{count + 1}/{amount}][/bold]', style='#EB2742')
	console.print(
		f'[bold][?][KFC] Объектов не прошедших валидацию: [/bold]{len(raw_data["searchResults"]) - len(output)}',
		style='#EB2742')
	return output


def parse() -> None:
	tprint('KFC', font='cybermedium')
	console.print("[bold][+][KFC] Начинаю парсить...[/bold]", style='#EB2742')
	raw_data = get_request(URL_POINT)
	data = get_data(raw_data)
	console.print(
		f'[bold][?][KFC] Всего объектов записано: [/bold]{len(data)}', style='#EB2742')

	console.print('[bold][+][KFC] Парсинг окончен![/bold]\n', style='#16C60C')


if __name__ == '__main__':
	parse()
