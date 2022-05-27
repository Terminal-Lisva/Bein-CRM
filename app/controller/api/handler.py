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
	def handle(self) -> Optional[Tuple[Dict[str, Any], int]]:
		"""Обрабатывает соответствующий запрос."""

	def _set_handler_error(self, source: str, type: str, enum: Enum) -> None:
		"""Устанавливает ошибку обработчика."""
		self._handler_error = source, type, enum.value

	def get_handler_error(self) -> Optional[Tuple[str, str, int]]:
		"""Получает ошибку обработчика."""
		return self._handler_error


class AuthenticationErrors(Enum):
	"""Ошибки аутентификации"""
	NO_AUTHENTICATION = 1


class HandlerRequestWithAuthentication(HandlerRequest, ABC):
	"""Обработчик запроса с аутентификацией пользователя"""

	def __init__(self):
		super().__init__()
		self._authentication_user = UserAuthenticationInfo()

	def _check_authentication_user(self) -> bool:
		"""Проверяет аутентификацию пользователя.
		Если пользователь не аутентифицирован
		устанавливает соответствующую ошибку операции."""
		if not self._authentication_user:
			self._set_handler_error(
				source="CookieSession/CookieAuth",
				type="NO_AUTHENTICATION",
				enum=AuthenticationErrors.NO_AUTHENTICATION
			)
			return False
		return True


class PermissionErrors(Enum):
	"""Ошибки разрешения"""
	NO_PERMISSION = 1


class HandlerRequestWithCheckID(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса с проверкой ID"""

	def __init__(self):
		super().__init__()

	def _check_user_id(self, user_id: int) -> bool:
		"""Проверяет аутентификацию пользователя.
		Сверяет входную ID пользователя с ID из аутентификации."""
		if not self._check_authentication_user():
			return False
		elif user_id != self._authentication_user.id:
			self._set_handler_error(
				source=f"id: {user_id}",
				type="NO_PERMISSION",
				enum=PermissionErrors.NO_PERMISSION
			)
			return False
		return True
