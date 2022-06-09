import datetime
import json
import sys
from pathlib import Path

from rich.console import Console


def save_json(name: str):
	def main_wrapper(func):
		def wrapper(*args, **kwargs):
			console = Console()
			time_now = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
			result = func(*args, **kwargs)
			with open(f'log/{time_now}_{name}.json', 'w', encoding='utf-8') as file:
				json.dump(result, file, indent=3, ensure_ascii=False)
			console.print(f'[+][JSON] Файл {name} был сохранен по пути:', style='#318CE7')
			console.print(f'[?][JSON] {Path(sys.path[0], "log")}', style='#F4CA16')
			return result

		return wrapper

	return main_wrapper
