from typing import Tuple, Union
from abc import ABC, abstractmethod
import base64
from utilities.other import HashingData


class CookieError(Exception):
    pass


class CreatorCookie(ABC):
	"""Создатель куки"""

	@abstractmethod
	def creates(self) -> str:
		"""Создает куку."""
		raise NotImplementedError()
	
	def _encrypts_data(self, data: str) -> str:
		"""Зашифровывает данные стандартом base64."""
		return base64.b64encode(data.encode()).decode()


class CreatorCookieSession(CreatorCookie):
	"""Создатель куки сессии"""

	__hashing_data: HashingData

	def __init__(self):
		self.__hashing_data = HashingData()

	def creates(self, user_id: int) -> str:
		"""Создает куку сессии."""
		hashed_user_id = self.__hashing_data.calculate_hash(user_id)
		data_format_for_encryption = f'{user_id}.{hashed_user_id}'
		data_encryption = self._encrypts_data(data_format_for_encryption)
		return data_encryption
	

class CreatorCookieAuth(CreatorCookie):
	"""Создатель куки авторизации"""

	def creates(self, email: str, hashed_password: str) -> str:
		"""Создает куку авторизации."""
		data_format_for_encryption = f'{email}&{hashed_password}'
		data_encryption = self._encrypts_data(data_format_for_encryption)
		return data_encryption


class GetterDataFromCookies(ABC):
	"""Получатель данных из кук"""

	@abstractmethod
	def get(self, cookie: str):
		"""Получает данные из куки."""
		raise NotImplementedError()
	
	def _decrypts_data(self, data: str) -> str:
		"""Расшифровывает данные, зашифрованные стандартом base64."""
		try:
			return base64.b64decode(data.encode() + b'===').decode()
		except (UnicodeDecodeError, Exception):
			return ""
	

class GetterDataFromCookieSession(GetterDataFromCookies):
	"""Получатель данных из куки сессии"""

	def get(self, cookie: str) -> Tuple[Union[int, str]]:
		"""Получает данные из куки сессии."""
		data_decryption = self._decrypts_data(cookie)
		split_data_decryption = data_decryption.split('.')
		if len(split_data_decryption) != 2: raise CookieError
		user_id = int(split_data_decryption[0])
		hashed_user_id = split_data_decryption[1]
		return user_id, hashed_user_id


class GetterDataFromCookieAuth(GetterDataFromCookies):
	"""Получатель данных из куки авторизации"""

	def get(self, cookie: str) -> Tuple[str]:
		"""Получает данные из куки авторизации."""
		data_decryption = self._decrypts_data(cookie)
		split_data_decryption = tuple(data_decryption.split('&'))
		if len(split_data_decryption) != 2: raise CookieError
		email, hashed_password = split_data_decryption
		return email, hashed_password

