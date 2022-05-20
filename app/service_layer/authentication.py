from abc import ABC, abstractmethod
from typing import Optional
from .cookies import CookieError, GetterDataFromCookies, GetterDataFromCookieSession, GetterDataFromCookieAuth, CreatorCookieSession, CreatorCookieAuth
from utilities.other import HashingData, records_log_user_authentication
from enum import Enum
from dataclasses import dataclass
from utilities.validations import ValidationEmail, ValidationPassword
from database import user_db


class GetterUserIDFromCookies(ABC):
	"""Базовый класс для получения ID пользователя из кук"""

	_data_from_cookie: GetterDataFromCookies

	def __init__(self, data_from_cookie):
		self._data_from_cookie = data_from_cookie()
	
	@abstractmethod
	def get(self, cookie: str) -> Optional[int]:
		"""Получает id пользователя из куки."""
		raise NotImplementedError()


class GetterUserIDFromCookieSession(GetterUserIDFromCookies):
	"""Класс для получения ID пользователя из куки сессии"""

	__hashing_data: HashingData

	def __init__(self):
		super().__init__(GetterDataFromCookieSession)
		self.__hashing_data = HashingData()
	
	def get(self, cookie: Optional[str]) -> Optional[int]:
		"""Получает id пользователя из куки сессии."""
		if cookie is None:
			return None
		try:
			user_id, hashed_user_id = self._data_from_cookie.get(cookie)
		except CookieError:
			return None
		if hashed_user_id != self.__hashing_data.calculate_hash(user_id):
			return None
		return user_id


class GetterUserIDFromCookieAuth(GetterUserIDFromCookies):
	"""Класс для получения ID пользователя из куки авторизации"""

	def __init__(self):
		super().__init__(GetterDataFromCookieAuth)

	def get(self, cookie: Optional[str]) -> Optional[int]:
		"""Получает id пользователя из куки авторизации."""
		if cookie is None:
			return None
		try:
			email, hashed_password = self._data_from_cookie.get(cookie)
		except CookieError:
			return None
		user_id = user_db.get_user_id((email, hashed_password))
		return user_id

@dataclass
class UserAuthenticationInfo:
	"""Информация об аутентификации пользователя"""

	user_id: Optional[int] = None
	cookie_session: Optional[str] = None
	cookie_auth: Optional[str] = None

	def __bool__(self):
		return self.user_id is not None


class Authentication(ABC):
	"""Аутентификация пользователя"""
	
	@abstractmethod
	def get_user_authentication_info(self) -> UserAuthenticationInfo:
		"""Получает информацию об аутентификации пользователя."""
		raise NotImplementedError()


class EnumErrors(Enum):
    """Перечисление ошибок"""
    NOT_VALID_EMAIL = 8
    NOT_VALID_PASSWORD = 9
    NOT_USER = 10


class AuthenticationByEmailAndPassword(Authentication):
	"""Аутентификация пользователя по емайлу и паролю"""

	__email: str
	__password: str
	__validation_email: ValidationEmail
	__validation_password: ValidationPassword
	__hashing_data: HashingData
	__creator_cookie_session: CreatorCookieSession
	__creator_cookie_auth: CreatorCookieAuth
	__operation_error: Optional[int]
	
	def __init__(self, email, password):
		self.__email = email
		self.__password = password
		self.__validation_email = ValidationEmail(email)
		self.__validation_password = ValidationPassword(password)
		self.__hashing_data = HashingData()
		self.__creator_cookie_session = CreatorCookieSession()
		self.__creator_cookie_auth = CreatorCookieAuth()
		self.__operation_error = None

	def get_user_authentication_info(self) -> UserAuthenticationInfo:
		"""Получает информацию об аутентификации пользователя."""
		if not self.__check_validation_email() or not self.__check_validation_password():
			return UserAuthenticationInfo()
		hashed_password = self.__hashing_data.calculate_hash(self.__password)
		user_id = self.__get_user_id_from_db(hashed_password)
		if user_id is None:
			return UserAuthenticationInfo()
		cookie_session = self.__creator_cookie_session.creates(user_id)
		cookie_auth = self.__creator_cookie_auth.creates(self.__email, hashed_password)
		records_log_user_authentication(user_id, type_auth='Email&Password')
		return UserAuthenticationInfo(user_id, cookie_session, cookie_auth)
	
	def __check_validation_email(self) -> bool:
		"""Проверяет полученный email на валидность. В случае отрицательного результата проверки устанавливает соответствующую ошибку операции."""
		if not (result := self.__validation_email.get_result()):
			self.__set_operation_error(EnumErrors.NOT_VALID_EMAIL)
		return result
	
	def __check_validation_password(self) -> bool:
		"""Проверяет полученный пароль на валидность. В случае отрицательного результата проверки устанавливает соответствующую ошибку операции."""
		if not (result := self.__validation_password.get_result()):
			self.__set_operation_error(EnumErrors.NOT_VALID_PASSWORD)
		return result
	
	def __get_user_id_from_db(self, hashed_password: str) -> Optional[int]:
		"""Получает id пользователя из базы данных. Если пользователь отсутствует в базе данных устанавливает соответствующую ошибку операции."""
		user_id = user_db.get_user_id((self.__email, hashed_password))
		if user_id is None:
			self.__set_operation_error(EnumErrors.NOT_USER)
		return user_id
			
	def __set_operation_error(self, error_type: EnumErrors) -> None:
		"""Устанавливает ошибку операции."""
		self.__operation_error = error_type.value

	def get_operation_error(self) -> Optional[int]:
		"""Получает ошибку операции."""
		return self.__operation_error


class AuthenticationByCookieSession(Authentication):
	"""Аутентификация пользователя по куке сессии"""

	__cookie_session: Optional[str]
	__getter_user_id_from_cookie_session: GetterUserIDFromCookieSession

	def __init__(self, cookie_session):
		self.__cookie_session = cookie_session
		self.__getter_user_id_from_cookie_session = GetterUserIDFromCookieSession()
	
	def get_user_authentication_info(self) -> UserAuthenticationInfo:
		"""Получает информацию об аутентификации пользователя."""
		user_id = self.__getter_user_id_from_cookie_session.get(self.__cookie_session)
		if user_id is None:
			return UserAuthenticationInfo()
		records_log_user_authentication(user_id, type_auth='CookieSession')
		return UserAuthenticationInfo(user_id)
			

class AuthenticationByCookieAuth(Authentication):
	"""Аутентификация пользователя по куке авторизации"""

	__cookie_auth: Optional[str]
	__getter_user_id_from_cookie_auth: GetterUserIDFromCookieAuth
	__creator_cookie_session: CreatorCookieSession

	def __init__(self, cookie_auth):
		self.__cookie_auth = cookie_auth
		self.__getter_user_id_from_cookie_auth = GetterUserIDFromCookieAuth()
		self.__creator_cookie_session = CreatorCookieSession()

	def get_user_authentication_info(self) -> UserAuthenticationInfo:
		"""Получает информацию об аутентификации пользователя."""
		user_id = self.__getter_user_id_from_cookie_auth.get(self.__cookie_auth)
		if user_id is None:
			return UserAuthenticationInfo()
		cookie_session = self.__creator_cookie_session.creates(user_id)
		records_log_user_authentication(user_id, type_auth='CookieAuth')
		return UserAuthenticationInfo(user_id, cookie_session)


class AuthenticationByCookies(Authentication):
	"""Аутентификация пользователя по кукам"""

	__cookie_session: Optional[str]
	__cookie_auth: Optional[str]
	__getter_user_id_from_cookie_session: GetterUserIDFromCookieSession
	__getter_user_id_from_cookie_auth: GetterUserIDFromCookieAuth
	__creator_cookie_session: CreatorCookieSession

	def __init__(self, cookie_session, cookie_auth):
		self.__cookie_session = cookie_session
		self.__cookie_auth = cookie_auth
		self.__getter_user_id_from_cookie_session = GetterUserIDFromCookieSession()
		self.__getter_user_id_from_cookie_auth = GetterUserIDFromCookieAuth()
		self.__creator_cookie_session = CreatorCookieSession()
	
	def get_user_authentication_info(self) -> UserAuthenticationInfo:
		"""Получает информацию об аутентификации пользователя."""
		user_id_from_cookie_session = self.__getter_user_id_from_cookie_session.get(self.__cookie_session)
		if user_id_from_cookie_session is not None:
			return UserAuthenticationInfo(user_id_from_cookie_session)
		user_id_from_cookie_auth = self.__getter_user_id_from_cookie_auth.get(self.__cookie_auth)
		if user_id_from_cookie_auth is None:
			return UserAuthenticationInfo()
		cookie_session = self.__creator_cookie_session.creates(user_id_from_cookie_auth)
		return UserAuthenticationInfo(user_id_from_cookie_auth, cookie_session)