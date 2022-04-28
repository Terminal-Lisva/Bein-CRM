from typing import *
from abc import ABC, abstractmethod
from .enums import Errors
import hmac
import base64
from hashlib import sha256
from flask import jsonify


class Response(ABC):
	"""Ответ (абстрактный класс)"""

	@abstractmethod
	def create_response(self):
		"""Создает ответ"""
		raise NotImplementedError()


class ErrorResponse(Response):
	"""Ответ - ошибка"""

	def __init__(self, errors: Errors):
		self.__errors = errors

	def create_response(self, error_code: int) -> Dict[str, Dict[str, Union[str, int]]]:
		"""Создает ответ (реализованный метод)"""
		return {
			"error": {
				"name": self.__errors.value[error_code],
				"code": error_code
			}
		}


class SuccessResponse(Response):
	"""Ответ - успех"""

	def create_response(self, value: Union[list, bool]) -> Dict[str, Dict[str, Union[list, bool]]]:
		"""Создает ответ (реализованный метод)"""
		return {
			"success": {
				"value": value,
			}
		}


def get_error_http():
	"""Получает ошибку HTTP"""
	return jsonify(ErrorResponse(Errors.app).create_response(error_code=1))


class HashingData:
	"""Хеширование данных"""

	__key = "qwerty123"
	__salt = "123123"

	def __init__(self, data: Any) -> str:
		self.__data = data

	def calculate_hash(self) -> str:
		"""Вычисляет хэш по алгоритму SHA256"""
		salted_string = str(self.__data) + HashingData.__salt
		return hmac.new(
			HashingData.__key.encode(),
			msg=salted_string.encode(),
			digestmod=sha256
		).hexdigest().upper()


class DataCrypt:
	"""Криптография данных"""

	def encrypts_data(self, data: str) -> str:
		"""Зашифровывает данные стандартом base64"""
		return base64.b64encode(data.encode()).decode()

	def decrypts_data(self, data: str) -> str:
		"""Расшифровывает данные, зашифрованные стандартом base64"""
		return base64.b64decode(data.encode()).decode()


class Cookie(ABC):
	"""Кука (абстрактный класс)"""

	@abstractmethod
	def creates_cookie(self):
		"""Создает куку (абстрактный метод)"""
		raise NotImplementedError()

	@abstractmethod
	def get_data_from_cookie(self):
		"""Получает данные из куки (абстрактный метод)"""
		raise NotImplementedError()


class CookieAuthentication(Cookie):
	"""Кука для аутентификации"""

	def creates_cookie(
		self, 
		email: str, 
		hashed_password: str
	) -> str:
		"""Создает куку (реализованный метод)"""
		data_format_for_encryption = f'{email}&{hashed_password}'
		data_encryption = DataCrypt().encrypts_data(data_format_for_encryption)
		return data_encryption

	def get_data_from_cookie(self, cookie: str) -> Tuple[str]:
		"""Получает данные из куки (реализованный метод)"""
		data_decryption = DataCrypt().decrypts_data(cookie)
		split_data_decryption = tuple(data_decryption.split('&'))
		assert len(split_data_decryption) == 2
		email, hashed_password = split_data_decryption
		return email, hashed_password


class CookieSession(Cookie):
	"""Кука для сессии"""

	def creates_cookie(self, user_id: int) -> str:
		"""Создает куку (реализованный метод)"""
		hashed_user_id = HashingData(user_id).calculate_hash()
		data_format_for_encryption = f'{user_id}.{hashed_user_id}'
		data_encryption = DataCrypt().encrypts_data(data_format_for_encryption)
		return data_encryption

	def get_data_from_cookie(self, cookie: str) -> Tuple[int, str]:
		"""Получает данные из куки (реализованный метод)"""
		data_decryption = DataCrypt().decrypts_data(cookie)
		split_data_decryption = data_decryption.split('.')
		assert len(split_data_decryption) == 2
		user_id = int(split_data_decryption[0])
		hashed_user_id = split_data_decryption[1]
		return user_id, hashed_user_id