from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Mapping, Any, TypedDict, Protocol
from controller.api.errors import Errors
from controller.service_layer.authentication_info import UserAuthenticationInfo
from database.models.database import db


@dataclass(slots=True, frozen=True)
class Error:
	source: str
	type: str
	message: str


@dataclass(slots=True, frozen=False)
class HandlerResult:
	document: Mapping[str, Any] | None = None
	status_code: int | None = None
	error: Error | None = None

	def __bool__(self) -> bool:
		return self.document is not None


class HandlerRequest(Protocol):
	"""Базовый класс - Обработчик запроса"""

	def handle(self) -> HandlerResult:
		"""Обрабатывает соответствующий запрос."""
		...


#class AuthenticationErrors(Enum):
#	"""Ошибки аутентификации"""
#	NO_AUTHENTICATION = 1


class HandlerRequestWithAuthentication(ABC):
	"""Обработчик запроса с аутентификацией пользователя"""

	_authentication_user: UserAuthenticationInfo
	_handler_result: HandlerResult

	def __init__(self):
		self._authentication_user = UserAuthenticationInfo()
		self._handler_result = HandlerResult()

	def _set_error_in_handler_result(self, source: str, error: Errors) -> None:
		"""Устанавливает ошибку в результат обработчика."""
		message, status_code = error.value
		self._handler_result.error = Error(
			source=source, type=error.name, message=message
		)
		self._handler_result.status_code = status_code

	def _check_authentication_user(self) -> bool:
		"""Проверяет аутентификацию пользователя.
		Если пользователь не аутентифицирован
		устанавливает соответствующую ошибку операции."""
		if not self._authentication_user:
			self._set_error_in_handler_result(
				source="CookieSession/CookieAuth",
				error=Errors.NO_AUTHENTICATION
			)
			return False
		return True


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
			self._set_error_in_handler_result(
				source="",
				error=Errors.NO_PERMISSION_RESOURCE
			)
		return True


class HandlerError(Exception):
	pass


class HandlerRequestGetData(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса получения данных"""

	def __init__(self):
		super().__init__()

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на получение данных."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			self._handler_result.document = self._create_document()
		except HandlerError:
			return self._handler_result
		self._handler_result.status_code = 200
		return self._handler_result

	@abstractmethod
	def _create_document(self) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()
