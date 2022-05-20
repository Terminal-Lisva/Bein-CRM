from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple
from utilities.validations import Validation
from enum import Enum


#Логика получения ответа от страницы:
class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_operation_error: Optional[Tuple[int, str]]

	def __init__(self):
		self._operation_error = None

	@abstractmethod
	def handle(self) -> Optional[Union[bool, Tuple[str]]]:
		"""Обрабатывает соответствующий запрос."""
		raise NotImplementedError()

	def _check_validation_value(self, value: str, validation: Validation, enum_error: Enum, type_error: str):
		"""Проверяет значение на валидацию."""
		if not (result := validation(value).get_result()):
			self._set_operation_error(enum_error, type_error)
		return result

	def _set_operation_error(self, enum_error: Enum, type_error: str) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = enum_error.value, type_error

	def get_operation_error(self) -> Optional[Tuple[int, str]]:
		"""Получает ошибку операции."""
		return self._operation_error


class AppErrors(Enum):
	"""Ошибки приложения"""
	NOT_AUTHENTICATION = 3


class HandlerWithAuthentication(HandlerRequest):
    """Обработчик запроса с аутентификацией"""

    def __init__(self):
        super().__init__()
        self.__authentication_info = AuthenticationInfo()

    def _get_user_id(self) -> Optional[int]:
        """Получает id пользователя из информации аутентификации. Если пользователь отсутствует устанавливает соответствующую ошибку операции."""
        user_id = self.__authentication_info.user_id
		if user_id is None:
			self._set_operation_error(error_type=AppErrors.NOT_AUTHENTICATION, type_error="app")
		return user_id