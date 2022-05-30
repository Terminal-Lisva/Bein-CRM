from abc import ABC, abstractmethod
import re


class Validation(ABC):
	"""Валидация"""

	@abstractmethod
	def get_result(self) -> bool:
		"""Получает результат валидации."""
		raise NotImplementedError()


class ValidationInvitationToken(Validation):
	"""Валидация токена приглашения"""

	__invitation_token: str

	def __init__(self, invitation_token):
		self.__invitation_token = invitation_token

	def get_result(self) -> bool:
		"""Получает результат."""
		return len(self.__invitation_token) == 32


class ValidationPassword(Validation):
	"""Валидация пароля"""

	__password: str

	def __init__(self, password):
		self.__password = password

	def get_result(self) -> bool:
		"""Получает результат."""
		if not 8 <= len(self.__password) <= 128:
			return False
		pattern = re.compile(
			"""
			^(?!.*\s+) #Дальше проверку не выполняю, если есть пробельный символ
			(?=(.*[A-Z]+)) #Минимум 1 алфавитный символ в верхнем регистре
			(?=(.*[a-z]+)) #Минимум 1 алфавитный символ в нижнем регистре
			(?=(.*\d+)) #Минимум 1 цифра
			""", re.VERBOSE)
		match = pattern.search(self.__password)
		return match is not None


class ValidationEmail(Validation):
	"""Валидация электронной почты"""

	__email: str

	def __init__(self, email):
		self.__email = email

	def get_result(self) -> bool:
		"""Получает результат."""
		if not 8 <= len(self.__email) <= 256:
			return False
		pattern = re.compile(
			"""
			^(?!.*\s+) #Дальше проверку не выполняю, если есть пробельный символ
			[\w\d.+-]+ #Имя пользователя
			@
			([\w\d.]+\.)+ #Префикс имени домена
			(ru|su)	#Домены верхнего уровня
			""", re.VERBOSE)
		match = pattern.match(self.__email)
		return match is not None


class ValidationFIO(Validation):
	"""Валидация ФИО"""

	__fio: str

	def __init__(self, fio):
		self.__fio = fio

	def get_result(self) -> bool:
		"""Получает результат."""
		fio_split = self.__fio.split(" ")
		if len(fio_split) != 3:
			return False
		pattern = re.compile('^(?!.*\W+)^(?!.*\d+)')
		for initial in fio_split:
			match = pattern.match(initial)
			if match is None:
				return False
			first_character = initial[0]
			if first_character.islower():
				return False
		return True
