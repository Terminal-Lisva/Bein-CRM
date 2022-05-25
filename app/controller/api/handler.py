from enum import Enum
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, Dict, Any, List
from utilities.validations import Validation
from controller.service_layer.authentication_info import UserAuthenticationInfo


#Логика получения ответа:
class HandlerError(Exception):
	pass


class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_handler_error: Optional[Tuple[str, str, int]]

	def __init__(self):
		self._handler_error = None

	@abstractmethod
	def handle(self) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
		"""Обрабатывает соответствующий запрос."""
		raise NotImplementedError()

	def _check(self, value: bool, source: str, type: str, enum: Enum) -> bool:
		"""Устанавливает соответствующую ошибку если значение ложное."""
		if not value:
			self._set_handler_error(source, type, enum)
		return value

	def _set_handler_error(self, source: str, type: str, enum: Enum) -> None:
		"""Устанавливает ошибку обработчика."""
		self._handler_error = source, type, enum.value

	def get_handler_error(self) -> Optional[Tuple[str, str, int]]:
		"""Получает ошибку обработчика."""
		return self._handler_error


class Errors(Enum):
	"""Ошибки"""
	NO_AUTHENTICATION = 1


class HandlerRequestWithAuthentication(HandlerRequest):
	"""Обработчик запроса с аутентификацией пользователя"""

	def __init__(self):
		super().__init__()
		self._authentication_user = UserAuthenticationInfo()

	def _check_authentication_user(self) -> bool:
		"""Проверяет аутентификацию пользователя."""
		return self._check(
			value=self._authentication_user,
			source="CookieSession/CookieAuth",
			type="REQUEST_AUTH",
			enum=Errors.NO_AUTHENTICATION
		)
