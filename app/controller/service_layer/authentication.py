from abc import ABC, abstractmethod
from typing import Optional, Tuple
from .cookies import (CookieError, GetterDataFromCookieSession,
GetterDataFromCookieAuth, CreatorCookieSession, CreatorCookieAuth)
from utilities.other import HashingData, records_log_user_authentication
from enum import Enum
from utilities.validations import ValidationEmail, ValidationPassword
from database import user_db


class GetterUserIDFromCookies(ABC):
	"""Базовый класс для получения ID пользователя из кук"""

	@abstractmethod
	def get(self, cookie: Optional[str]) -> Optional[int]:
		"""Получает id пользователя из куки."""
		raise NotImplementedError()


class GetterUserIDFromCookieSession(GetterUserIDFromCookies):
	"""Класс для получения ID пользователя из куки сессии"""

	__data_from_cookie: GetterDataFromCookieSession

	def __init__(self):
		self.__data_from_cookie = GetterDataFromCookieSession()

	def get(self, cookie: Optional[str]) -> Optional[int]:
		"""Получает id пользователя из куки сессии."""
		if cookie is None:
			return None
		try:
			user_id, hashed_user_id = self.__data_from_cookie.get(cookie)
		except CookieError:
			return None
		if hashed_user_id != HashingData().calculate_hash(user_id):
			return None
		return user_id


class GetterUserIDFromCookieAuth(GetterUserIDFromCookies):
	"""Класс для получения ID пользователя из куки авторизации"""

	__data_from_cookie: GetterDataFromCookieAuth

	def __init__(self):
		self.__data_from_cookie = GetterDataFromCookieAuth()

	def get(self, cookie: Optional[str]) -> Optional[int]:
		"""Получает id пользователя из куки авторизации."""
		if cookie is None:
			return None
		try:
			email, hashed_password = self.__data_from_cookie.get(cookie)
		except CookieError:
			return None
		user_id = user_db.get_user_id((email, hashed_password))
		return user_id


class Authentication(ABC):
	"""Аутентификация пользователя"""

	@abstractmethod
	def authenticates_user(self) -> Optional[int]:
		"""Аутентифицирует пользователя."""
		raise NotImplementedError()


class ValidationErrors(Enum):
	"""Ошибки валидации"""
	NOT_VALID_PASSWORD = 2
	NOT_VALID_EMAIL = 3


class NoDataErrors(Enum):
	"""Ошибки отсутствия данных"""
	NO_USER = 3


class AuthenticationByEmailAndPassword(Authentication):
	"""Аутентификация пользователя по емайлу и паролю"""

	__email: str
	__password: str
	__cookie_session: Optional[str]
	__cookie_auth: Optional[str]
	__operation_error: Optional[Tuple[str, str, int]]

	def __init__(self, email, password):
		self.__email = email
		self.__password = password
		self.__cookie_session = None
		self.__cookie_auth = None
		self.__operation_error = None

	def authenticates_user(self) -> Optional[int]:
		"""Аутентифицирует пользователя."""
		if (not self.__check_validation_email()
			or not self.__check_validation_password()):
			return None
		hashed_password = HashingData().calculate_hash(self.__password)
		user_id = self.__get_user_id_from_db(hashed_password)
		if user_id is None:
			return None
		self.__set_cookie_session(user_id)
		self.__set_cookie_auth(hashed_password)
		records_log_user_authentication(user_id, type_auth='Email&Password')
		return user_id

	def __check_validation_email(self) -> bool:
		"""Проверяет полученный email на валидность. В случае отрицательного
		результата проверки устанавливает соответствующую ошибку операции."""
		if not (result := ValidationEmail(self.__email).get_result()):
			self.__set_operation_error(
				source=f"Email: {self.__email}",
				type="VALIDATION",
				enum=ValidationErrors.NOT_VALID_EMAIL)
		return result

	def __check_validation_password(self) -> bool:
		"""Проверяет полученный пароль на валидность. В случае отрицательного
		результата проверки устанавливает соответствующую ошибку операции."""
		if not (result := ValidationPassword(self.__password).get_result()):
			self.__set_operation_error(
				source=f"Пароль: {self.__password}",
				type="VALIDATION",
				enum=ValidationErrors.NOT_VALID_PASSWORD)
		return result

	def __get_user_id_from_db(self, hashed_password: str) -> Optional[int]:
		"""Получает id пользователя из базы данных.
		Если пользователь отсутствует в базе данных устанавливает
		соответствующую ошибку операции."""
		user_id = user_db.get_user_id((self.__email, hashed_password))
		if user_id is None:
			self.__set_operation_error(
				source=f"Email: {self.__email}, Пароль: {self.__password}",
				type="NO_DATA",
				enum=NoDataErrors.NO_USER)
		return user_id

	def __set_cookie_session(self, user_id: int) -> None:
		"""Устанавливает куки сессии."""
		self.__cookie_session = CreatorCookieSession().creates(user_id)

	def get_cookie_session(self) -> Optional[str]:
		"""Получает куки сессии."""
		return self.__cookie_session

	def __set_cookie_auth(self, hashed_password: str) -> None:
		"""Устанавливает куки авторизации."""
		self.__cookie_auth = CreatorCookieAuth().creates(
			self.__email, hashed_password)

	def get_cookie_auth(self) -> Optional[str]:
		"""Получает куки авторизации."""
		return self.__cookie_auth

	def __set_operation_error(self, source: str, type: str, enum: Enum) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = source, type, enum.value

	def get_operation_error(self) -> Optional[Tuple[str, str, int]]:
		"""Получает ошибку операции."""
		return self._operation_error


class AuthenticationByCookieSession(Authentication):
	"""Аутентификация пользователя по куке сессии"""

	__cookie_session: Optional[str]

	def __init__(self, cookie_session):
		self.__cookie_session = cookie_session

	def authenticates_user(self) -> Optional[int]:
		"""Аутентифицирует пользователя."""
		user_id = GetterUserIDFromCookieSession().get(self.__cookie_session)
		if user_id is None:
			return None
		records_log_user_authentication(user_id, type_auth='CookieSession')
		return user_id


class AuthenticationByCookieAuth(Authentication):
	"""Аутентификация пользователя по куке авторизации"""

	__cookie_auth: Optional[str]
	__cookie_session: Optional[str]

	def __init__(self, cookie_auth):
		self.__cookie_auth = cookie_auth
		self.__cookie_session = None

	def authenticates_user(self) -> Optional[int]:
		"""Аутентифицирует пользователя."""
		user_id = GetterUserIDFromCookieAuth().get(self.__cookie_auth)
		if user_id is None:
			return None
		self.__set_cookie_session(user_id)
		records_log_user_authentication(user_id, type_auth='CookieAuth')
		return user_id

	def __set_cookie_session(self, user_id: int) -> None:
		"""Устанавливает куки сессии."""
		self.__cookie_session = CreatorCookieSession().creates(user_id)

	def get_cookie_session(self) -> Optional[str]:
		"""Получает куки сессии."""
		return self.__cookie_session


class AuthenticationByCookies(Authentication):
	"""Аутентификация пользователя по кукам"""

	__cookie_session: Optional[str]
	__cookie_auth: Optional[str]

	def __init__(self, cookie_session, cookie_auth):
		self.__cookie_session = cookie_session
		self.__cookie_auth = cookie_auth

	def authenticates_user(self) -> Optional[int]:
		"""Аутентифицирует пользователя."""
		user_id_from_cookie_session = GetterUserIDFromCookieSession().get(
			self.__cookie_session)
		if user_id_from_cookie_session is not None:
			return user_id_from_cookie_session
		user_id_from_cookie_auth = GetterUserIDFromCookieAuth().get(
			self.__cookie_auth)
		if user_id_from_cookie_auth is None:
			return None
		self.__set_cookie_session(user_id_from_cookie_auth)
		return user_id_from_cookie_auth

	def __set_cookie_session(self, user_id: int) -> None:
		"""Устанавливает куки сессии."""
		self.__cookie_session = CreatorCookieSession().creates(user_id)

	def get_cookie_session(self) -> Optional[str]:
		"""Получает куки сессии."""
		return self.__cookie_session
