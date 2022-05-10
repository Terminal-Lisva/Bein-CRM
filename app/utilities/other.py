from typing import Any
import hmac

from hashlib import sha256


class HashingData:
	"""Хеширование данных"""

	__key = "qwerty123"
	__salt = "123123"

	def calculate_hash(self, string: Any) -> str:
		"""Вычисляет хэш по алгоритму SHA256."""
		salted_string = str(string) + self.__salt
		return hmac.new(
			HashingData.__key.encode(),
			msg=salted_string.encode(),
			digestmod=sha256
		).hexdigest().upper()