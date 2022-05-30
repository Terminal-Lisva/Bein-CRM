from dataclasses import dataclass
from flask import request
from utilities.const import prefix_api
from abc import ABC, abstractmethod
from typing import Any
from enum import Enum
from utilities.validations import Validation
from controller.service_layer.authentication_info import UserAuthenticationInfo


class ExcHandlerError(Exception):
	pass


@dataclass
class HandlerError:
	source: str | None = None
	type: str | None = None
	code: int | None = None


Response = dict[str, str | dict[str, str]]

@dataclass(slots=True, frozen=True)
class HandlerResult:
	response: Response | None = None
	status_code: int | None = None

	def __bool__(self) -> bool:
		return self.response is not None


def make_meta_data(href: str, type: str) -> dict[str, str]:
    """Создает мета-данные."""
    return {
        "href": request.url_root + prefix_api + href,
        "type": type
    }


class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_handler_error: HandlerError

	def __init__(self):
		self._handler_error = HandlerError()

	@abstractmethod
	def handle(self) -> HandlerResult:
		"""Обрабатывает соответствующий запрос."""

	def _set_handler_error(self, source: str, type: str, enum: Enum) -> None:
		"""Устанавливает ошибку обработчика."""
		self._handler_error.source = source
		self._handler_error.type = type
		self._handler_error.code = enum.value

	def get_handler_error(self) -> HandlerError:
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
		elif user_id != self._authentication_user.user_id:
			self._set_handler_error(
				source=f"id: {user_id}",
				type="NO_PERMISSION",
				enum=PermissionErrors.NO_PERMISSION
			)
			return False
		return True
