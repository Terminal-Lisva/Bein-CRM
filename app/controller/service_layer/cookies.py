from typing import Tuple, Union
from abc import ABC, abstractmethod
from utilities.other import HashingData, encrypts_data, decrypts_data


class CookieError(Exception):
	pass


class CreatorCookieSession():
	"""Создатель куки сессии"""

	@staticmethod
	def creates(user_id: int) -> str:
		"""Создает куку сессии."""
		hashed_user_id = HashingData().calculate_hash(user_id)
		data_format_for_encryption = f'{user_id}.{hashed_user_id}'
		data_encryption = encrypts_data(data_format_for_encryption)
		return data_encryption


class CreatorCookieAuth():
	"""Создатель куки авторизации"""

	@staticmethod
	def creates(email: str, hashed_password: str) -> str:
		"""Создает куку авторизации."""
		data_format_for_encryption = f'{email}&{hashed_password}'
		data_encryption = encrypts_data(data_format_for_encryption)
		return data_encryption


class GetterDataFromCookieSession():
	"""Получатель данных из куки сессии"""

	@staticmethod
	def get(cookie: str) -> Tuple[int, str]:
		"""Получает данные из куки сессии."""
		data_decryption = decrypts_data(cookie)
		split_data_decryption = data_decryption.split('.')
		if len(split_data_decryption) != 2: raise CookieError
		user_id = int(split_data_decryption[0])
		hashed_user_id = split_data_decryption[1]
		return user_id, hashed_user_id


class GetterDataFromCookieAuth():
	"""Получатель данных из куки авторизации"""

	@staticmethod
	def get(cookie: str) -> Tuple[str, str]:
		"""Получает данные из куки авторизации."""
		data_decryption = decrypts_data(cookie)
		split_data_decryption = tuple(data_decryption.split('&'))
		if len(split_data_decryption) != 2: raise CookieError
		email, hashed_password = split_data_decryption
		return email, hashed_password
