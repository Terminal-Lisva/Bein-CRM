from enum import Enum
from .handler import (HandlerRequestWithAuthentication, HandlerRequest,
HandlerError)
from models.user import UserModel, DataDict
from typing import Optional, Union, List, Dict
from utilities.validations import ValidationInvitationToken, ValidationPassword
from utilities.other import (records_log_user_registration,
records_log_user_restorer, HashingData)
from database import user_db


class AccessErrors(Enum):
	"""Ошибки доступа"""
	NO_PERMISSION_VIEW_USERS = 1


class ValidationErrors(Enum):
	"""Ошибки валидации"""
	NOT_VALID_TOKEN = 1
	NOT_VALID_PASSWORD = 2


class NoDataErrors(Enum):
	"""Ошибки отсутсвия данных"""
	NO_TOKEN = 1
	NO_USERS_DATA = 4


class AlreadyDataErrors(Enum):
	"""Ошибки в наличии данных"""
	USER_IS_BD = 1
	USER_IS_NOT_BD = 2


class HandlerRequestGetUsers(HandlerRequestWithAuthentication):
	"""Обработчик запроса получения пользователей"""

	__token: Optional[str]
	__user_model: UserModel

	def __init__(self, token):
		super().__init__()
		self.__token = token
		self.__user_model = UserModel()

	def handle(self) -> Optional[Union[DataDict, List[DataDict]]]:
		"""Обрабатывает запрос на получение пользователя"""
		if self._check_authentication_user():
			return self.__get_users_data(None)
		elif self._check(
			value=self.__token is not None,
			source=f"Session",
			type="NO_PERMISSION",
			enum=AccessErrors.NO_PERMISSION_VIEW_USERS
			) and self._check(
			value=ValidationInvitationToken(self.__token).get_result(),
			source=f"Токен приглашения: {self.__token}",
			type="VALIDATION",
			enum=ValidationErrors.NOT_VALID_TOKEN):
			return self.__get_users_data(self.__token)
		return None

	def __get_users_data(
		self,
		arg: Optional[str]) -> Union[DataDict, List[DataDict]]:
		"""Получает данные пользователей. Если данные отсутствуют в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		user_data = self.__user_model.get_data(arg)
		if user_data is None: #токен приглашения подделка
			self._set_handler_error(
				source=f"Не идентифицирован: {arg}",
				type="NO_DATA",
				enum=NoDataErrors.NO_USERS_DATA
			)
			raise HandlerError
		return user_data


class HandlerRequestAddUser(HandlerRequest):
	"""Обработчик запроса на добавление пользователя"""

	__token: str
	__password: str
	__user_model: UserModel

	def __init__(self, token, password):
		super().__init__()
		self.__token = token
		self.__password = password
		self.__user_model = UserModel()

	def handle(self) -> Optional[DataDict]:
		"""Обрабатывает запрос на регистрацию пользователя."""
		if not self._check(
			value=ValidationInvitationToken(self.__token).get_result(),
			source=f"Токен приглашения: {self.__token}",
			type="VALIDATION",
			enum=ValidationErrors.NOT_VALID_TOKEN
			) or not self._check(
			value=ValidationPassword(self.__password).get_result(),
			source=f"Пароль: {self.__token}",
			type="VALIDATION",
			enum=ValidationErrors.NOT_VALID_PASSWORD):
			return None
		user_id = self.__get_user_id_from_db()
		self.__add_user_to_db(user_id)
		user_data = self.__get_user_data(user_id)
		records_log_user_registration(user_id)
		return user_data

	def __get_user_id_from_db(self) -> int:
		"""Получает id пользователя из базы данных.
		Если пользователь отсутствует в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		user_id = user_db.get_user_id(self.__token)
		if user_id is None:
			self._set_handler_error(
				source=f"Токен приглашения: {self.__token}",
				type="NO_DATA",
				enum=NoDataErrors.NO_TOKEN
			)
			raise HandlerError
		return user_id

	def __add_user_to_db(self, user_id: int) -> None:
		"""Добавляет пользователя в базу данных.
		Если пользователь уже имеется в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		if not user_db.check_user_authentication(user_id):
			self._set_handler_error(
				source=f"id: {user_id}",
				type="ALREADY_DATA",
				enum=AlreadyDataErrors.USER_IS_BD
			)
			raise HandlerError
		hashed_password = HashingData().calculate_hash(self.__password)
		user_db.add_user_authentication(user_id, hashed_password)

	def __get_user_data(self, user_id: int) -> DataDict:
		"""Получает данные пользователя из модели."""
		user_data = self.__user_model.get_data(arg=user_id)
		return user_data


class HandlerRequestUsersPassword(HandlerRequest):
	"""Обработчик запроса на пароль"""

	__token: str
	__password: str

	def __init__(self, token, password):
		super().__init__()
		self.__token = token
		self.__password = password

	def handle(self) -> Optional[Dict[str, str]]:
		"""Обрабатывает запрос на восстановление пароля."""
		if not self._check(
			value=ValidationInvitationToken(self.__token).get_result(),
			source=f"Токен приглашения: {self.__token}",
			type="VALIDATION",
			enum=ValidationErrors.NOT_VALID_TOKEN
			) or not self._check(
			value=ValidationPassword(self.__password).get_result(),
			source=f"Пароль: {self.__password}",
			type="VALIDATION",
			enum=ValidationErrors.NOT_VALID_PASSWORD):
			return None
		user_id = self.__get_user_id_from_db()
		self.__restores_user_to_db(user_id)
		records_log_user_restorer(user_id)
		return {"message": "Пароль успешно восстановлен"}

	def __get_user_id_from_db(self) -> int:
		"""Получает id пользователя из базы данных.
		Если пользователь отсутствует в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		user_id = user_db.get_user_id(self.__token)
		if user_id is None:
			self._set_handler_error(
				source=f"Токен приглашения: {self.__token}",
				type="NO_DATA",
				enum=NoDataErrors.NO_TOKEN
			)
			raise HandlerError
		return user_id

	def __restores_user_to_db(self, user_id: int) -> None:
		"""Восстанавливает пользователя в базе данных.
		Если пользователя нет в базе данных
		устанавливает соответствующую ошибку операции и вызывает исключение."""
		if user_db.check_user_authentication(user_id):
			self._set_handler_error(
				source=f"id: {user_id}",
				type="ALREADY_DATA",
				enum=AlreadyDataErrors.USER_IS_NOT_BD
			)
			raise HandlerError
		user_db.remove_user_authentication(user_id)
		hashed_password = HashingData().calculate_hash(self.__password)
		user_db.add_user_authentication(user_id, hashed_password)
