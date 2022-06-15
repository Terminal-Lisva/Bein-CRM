from flask import request
from utilities.const import prefix_api


def make_href(path: str) -> str:
	"""Создает href."""
	return request.url_root + prefix_api + path
