from enum import Enum
from .handler import HandlerRequest, HandlerError
from models.account import AccountModel, AccountDataDict
from typing import Optional
from utilities.validations import ValidationInvitationToken, ValidationPassword
from utilities.other import (records_log_user_registration,
records_log_user_restorer, HashingData)
from database import db_auth


class ValidationErrors(Enum):
	"""Ошибки валидации"""
	NOT_VALID_TOKEN = 1
	NOT_VALID_PASSWORD = 2


class NoDataErrors(Enum):
	"""Ошибки отсутсвия данных"""
	NO_TOKEN = 1


class AlreadyDataErrors(Enum):
	"""Ошибки в наличии данных"""
	USER_IS_BD = 1
	USER_IS_NOT_BD = 2


class HandlerRequestAccountAccess(HandlerRequest):
	"""Обоработчик запроса доступа к аккаунту пользователя"""

	_token: str
	_password: str
	_account_model: AccountModel

	def __init__(self, token, password):
		super().__init__()
		self._token = token
		self._password = password
		self._account_model = AccountModel()

	def _check_request_data(self) -> bool:
		"""Проверяет данные из запроса."""
		if not ValidationInvitationToken(self._token).get_result():
			self._set_handler_error(
				source=f"Токен приглашения: {self._token}",
				type="VALIDATION",
				enum=ValidationErrors.NOT_VALID_TOKEN
			)
			return False
		elif not ValidationPassword(self._password).get_result():
			self._set_handler_error(
				source=f"Пароль: {self._password}",
				type="VALIDATION",
				enum=ValidationErrors.NOT_VALID_PASSWORD
			)
			return False
		return True

	def _get_user_id(self) -> int:
		"""Получает id пользователя из базы данных.
		Если пользователь отсутствует в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		user_id = db_auth.get_user_id(self._token)
		if user_id is None:
			self._set_handler_error(
				source=f"Токен приглашения: {self._token}",
				type="NO_DATA",
				enum=NoDataErrors.NO_TOKEN
			)
			raise HandlerError
		return user_id

	def _get_account_data(self, user_id: int) -> AccountDataDict:
		"""Получает данные аккаунта зарегистрированного пользователя."""
		account_data = self._account_model.get_data(user_id)
		return account_data


class HandlerRequestAddAccount(HandlerRequestAccountAccess):
	"""Обработчик запроса на добавление пользователя"""

	def __init__(self, token, password):
		super().__init__(token, password)

	def handle(self) -> Optional[AccountDataDict]:
		"""Обрабатывает запрос на регистрацию пользователя."""
		if not self._check_request_data(): return None
		user_id = self._get_user_id()
		self.__add_user_to_db(user_id)
		records_log_user_registration(user_id)
		return self._get_account_data(user_id)

	def __add_user_to_db(self, user_id: int) -> None:
		"""Добавляет пользователя в базу данных.
		Если пользователь уже имеется в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		if not db_auth.check_user_authentication(user_id):
			self._set_handler_error(
				source=f"id: {user_id}",
				type="ALREADY_DATA",
				enum=AlreadyDataErrors.USER_IS_BD
			)
			raise HandlerError
		hashed_password = HashingData().calculate_hash(self._password)
		db_auth.add_user_authentication(user_id, hashed_password)


class HandlerRequestRestoreAccount(HandlerRequestAccountAccess):
	"""Обработчик запроса на восстановление аккаунта"""

	def __init__(self, token, password):
		super().__init__(token, password)

	def handle(self) -> Optional[AccountDataDict]:
		"""Обрабатывает запрос на восстановление пароля."""
		if not self._check_request_data(): return None
		user_id = self._get_user_id()
		self.__restores_user_to_db(user_id)
		records_log_user_restorer(user_id)
		return self._get_account_data(user_id)

	def __restores_user_to_db(self, user_id: int) -> None:
		"""Восстанавливает пользователя в базе данных.
		Если пользователя нет в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		if db_auth.check_user_authentication(user_id):
			self._set_handler_error(
				source=f"id: {user_id}",
				type="ALREADY_DATA",
				enum=AlreadyDataErrors.USER_IS_NOT_BD
			)
			raise HandlerError
		db_auth.remove_user_authentication(user_id)
		hashed_password = HashingData().calculate_hash(self._password)
		db_auth.add_user_authentication(user_id, hashed_password)
