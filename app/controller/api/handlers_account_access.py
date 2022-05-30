from dataclasses import dataclass
from enum import Enum
from .handler import (HandlerRequest, ExcHandlerError, Response, HandlerResult,
make_meta_data)
from abc import ABC
from utilities.validations import ValidationInvitationToken, ValidationPassword
from utilities.other import (records_log_user_registration,
records_log_user_restorer, HashingData)
from database import db_auth
from database.models.user import Users


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


class HandlerRequestAccountAccess(HandlerRequest, ABC):
	"""Обоработчик запроса доступа к аккаунту пользователя"""

	_token: str
	_password: str

	def __init__(self, token, password):
		super().__init__()
		self._token = token
		self._password = password

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
			raise ExcHandlerError
		return user_id

	def _create_response(self, user_id: int) -> Response:
		"""Создает ответ от обработчика."""
		user = Users.query.get(user_id)
		return make_meta_data(
			href=f"/users/{user_id}/account",
			type="account") | {"email": user.email}


class HandlerRequestAddAccount(HandlerRequestAccountAccess):
	"""Обработчик запроса на добавление пользователя"""

	def __init__(self, token, password):
		super().__init__(token, password)

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на регистрацию пользователя."""
		if not self._check_request_data():
			return HandlerResult()
		user_id = self._get_user_id()
		self.__add_user_to_db(user_id)
		records_log_user_registration(user_id)
		response = self._create_response(user_id)
		return HandlerResult(response, status_code=201)

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
			raise ExcHandlerError
		hashed_password = HashingData().calculate_hash(self._password)
		db_auth.add_user_authentication(user_id, hashed_password)


class HandlerRequestRestoreAccount(HandlerRequestAccountAccess):
	"""Обработчик запроса на восстановление аккаунта"""

	def __init__(self, token, password):
		super().__init__(token, password)

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на восстановление пароля."""
		if not self._check_request_data():
			return HandlerResult()
		user_id = self._get_user_id()
		self.__restores_user_to_db(user_id)
		records_log_user_restorer(user_id)
		response = self._create_response(user_id)
		return HandlerResult(response, status_code=201)

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
			raise ExcHandlerError
		db_auth.remove_user_authentication(user_id)
		hashed_password = HashingData().calculate_hash(self._password)
		db_auth.add_user_authentication(user_id, hashed_password)
