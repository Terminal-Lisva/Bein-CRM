from enum import Enum
from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple
from utilities.validations import Validation
from .service_layer.user import User


#Логика получения ответа от страницы:
class Errors(Enum):
	"""Ошибки"""
	NO_AUTHENTICATION = 1


class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_operation_error: Optional[Tuple[str, str, int]]

	def __init__(self):
		self._operation_error = None

	@abstractmethod
	def handle(self) -> Optional[Union[bool, Tuple[str]]]:
		"""Обрабатывает соответствующий запрос."""
		raise NotImplementedError()

	def _check_validation_value(
		self,
		value: str,
		validation: Validation,
		source: str,
		type: str,
		enum: Enum
		) -> bool:
		"""Проверяет значение на валидацию."""
		if not (result := validation(value).get_result()):
			self._set_operation_error(source, type, enum)
		return result

	def _set_operation_error(self, source: str, type: str, enum: Enum) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = source, type, enum.value

	def get_operation_error(self) -> Optional[Tuple[str, str, int]]:
		"""Получает ошибку операции."""
		return self._operation_error


class HandlerWithUser(HandlerRequest):
	"""Обработчик запроса с пользователем"""

	def __init__(self):
		super().__init__()
		self._user = User()

	def _check_authentication_user(self) -> bool:
		"""Проверяет аутентификацию пользователя. Если аутентификация
		отсутствует устанавливает соответствующую ошибку операции."""
		if result := not self._user:
			self._set_operation_error(
				source="CookieSession/CookieAuth",
				type="REQUEST_AUTH",
				enum=Errors.NO_AUTHENTICATION
			)
		return result
