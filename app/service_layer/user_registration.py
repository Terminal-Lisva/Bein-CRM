from enum import Enum
from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, Dict
from utilities.validations import Validation, ValidationInvitationToken, ValidationPassword, ValidationFIO
from database import user_db
from utilities.other import HashingData, records_log_user_registration, records_log_user_restorer


class EnumErrors(Enum):
    """Перечисление ошибок"""
    NOT_VALID_TOKEN = 1
    NOT_TOKEN = 2
    NOT_VALID_PASSWORD = 3
    NOT_VALID_USER_NAME = 4
    NOT_USER_NAME = 5
    USER_IS_BD = 6
    USER_IS_NOT_BD = 7


class Registration(ABC):
	"""Регистрация"""

	_operation_error: Optional[int]

	def __init__(self):
		self._operation_error = None

	@abstractmethod
	def get_response(self) -> Optional[Union[bool, Tuple[str]]]:
		"""Получает соответствующий ответ."""
		raise NotImplementedError()

	def _check_validation_value(self, value: str, validation: Validation, error_type: EnumErrors):
		"""Проверяет значение на валидацию."""
		if not (result := validation(value).get_result()):
			self._set_operation_error(error_type)
		return result

	def _set_operation_error(self, error_type: EnumErrors) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = error_type.value

	def get_operation_error(self) -> Optional[int]:
		"""Получает ошибку операции."""
		return self._operation_error


class UserDataForRegistration(Registration):
	"""Данные пользователя для регистрации"""
	
	__invitation_token: str

	def __init__(self, request_data: Dict[str, str]):
		super().__init__()
		self.__invitation_token = request_data["invitation_token"]

	def get_response(self) -> Optional[Tuple[str]]:
		"""Получает данные пользователя для регистрации."""
		if not self._check_validation_value(
			value=self.__invitation_token,
			validation=ValidationInvitationToken,
			error_type=EnumErrors.NOT_VALID_TOKEN
			):
			return None
		user_data = self.__get_user_data_from_db()
		return user_data

	def __get_user_data_from_db(self) -> Optional[tuple]:
		"""Получает данные пользователя из базы данных. Если данные пользователя отсутствуют устанавливает соответствующую ошибку операции."""
		user_data = user_db.get_user_data(self.__invitation_token)
		if user_data is None:
			self._set_operation_error(EnumErrors.NOT_TOKEN)
		return user_data	


class UserRegistrator(Registration):
	"""Регистрация пользователя"""

	__invitation_token: str
	__password: str
	__hashing_data: HashingData

	def __init__(self, request_data: Dict[str, str]):
		super().__init__()
		self.__invitation_token = request_data["invitation_token"]
		self.__password = request_data["password"]
		self.__hashing_data = HashingData()

	def get_response(self) -> bool:
		"""Получает результат регистрации пользователя."""
		if not self._check_validation_value(
			value=self.__invitation_token,
			validation=ValidationInvitationToken,
			error_type=EnumErrors.NOT_VALID_TOKEN
			) or not self._check_validation_value(
			value=self.__password,
			validation=ValidationPassword,
			error_type=EnumErrors.NOT_VALID_PASSWORD
			):
			return False
		user_id = self.__get_user_id_from_db()
		if user_id is None:
			return False
		result = self.__add_user_to_db(user_id)
		if result: records_log_user_registration(user_id)
		return result
	
	def __get_user_id_from_db(self) -> Optional[int]:
		"""Получает id пользователя из базы данных. Если пользователь отсутствует в базе данных устанавливает соответствующую ошибку операции."""
		user_id = user_db.get_user_id(self.__invitation_token)
		if user_id is None:
			self._set_operation_error(EnumErrors.NOT_TOKEN)
		return user_id
	
	def __add_user_to_db(self, user_id: int) -> bool:
		"""Добавляет пользователя в базу данных. Если пользователь уже имеется в базе данных устанавливает соответствующую ошибку операции."""
		if not user_db.check_user_authentication(user_id):
			self._set_operation_error(EnumErrors.USER_IS_BD)
			return False
		hashed_password = self.__hashing_data.calculate_hash(self.__password)
		user_db.add_user_authentication(user_id, hashed_password)
		return True


class UserRestorer(Registration):
	"""Восстановитель пользователя"""

	__invitation_token: str
	__user_name: str
	__new_password: str
	__hashing_data: HashingData

	def __init__(self, request_data: Dict[str, str]):
		super().__init__()
		self.__invitation_token = request_data["invitation_token"]
		self.__user_name = request_data["user_name"]
		self.__new_password = request_data["new_password"]
		self.__hashing_data = HashingData()

	def get_response(self) -> bool:
		"""Получает результат восстановления пользователя."""
		if not self._check_validation_value(
			value=self.__invitation_token,
			validation=ValidationInvitationToken,
			error_type=EnumErrors.NOT_VALID_TOKEN
			) or not self._check_validation_value(
			value=self.__user_name,
			validation=ValidationFIO,
			error_type=EnumErrors.NOT_VALID_USER_NAME
			) or not self._check_validation_value(
			value=self.__new_password,
			validation=ValidationPassword,
			error_type=EnumErrors.NOT_VALID_PASSWORD
			):
			return False
		user_id = self.__get_user_id_from_db()
		if user_id is None:
			return False
		if not self.__has_user_name_in_db(user_id):
			return False
		result = self.__restores_user_to_db(user_id)
		if result: records_log_user_restorer(user_id)
		return result
	
	def __get_user_id_from_db(self) -> Optional[int]:
		"""Получает id пользователя из базы данных. Если пользователь отсутствует в базе данных устанавливает соответствующую ошибку операции."""
		user_id = user_db.get_user_id(self.__invitation_token)
		if user_id is None:
			self._set_operation_error(EnumErrors.NOT_TOKEN)
		return user_id
	
	def __has_user_name_in_db(self, user_id: int) -> bool:
		"""Проверяет полученное имя пользователя на соответствие с именем в базе данных. В случае отрицательного результата проверки устанавливает соответствующую ошибку операции."""
		user_name = user_db.get_user_fio(user_id)
		if not (result := self.__user_name == user_name):
			self._set_operation_error(EnumErrors.NOT_USER_NAME)
		return result

	def __restores_user_to_db(self, user_id: int) -> bool:
		"""Восстанавливает пользователя в базе данных. Если пользователя нет в базе данных устанавливает соответствующую ошибку операции."""
		if user_db.check_user_authentication(user_id):
			self._set_operation_error(EnumErrors.USER_IS_NOT_BD)
			return False
		user_db.remove_user_authentication(user_id)
		hashed_new_pas = self.__hashing_data.calculate_hash(self.__new_password)
		user_db.add_user_authentication(user_id, hashed_new_pas)
		return True
