from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Mapping, Any, TypedDict, Protocol, Callable
from controller.api.errors import Errors
from controller.service_layer.authentication_info import UserAuthenticationInfo
from database.models.database import db
from controller.api.query_string_parser import (QueryStringParser, FieldQuery,
ErrorQueryStringParsing)
from database.models.filters import GetterModelsUsingCustomFilter
from pydantic import BaseModel, ValidationError
import sqlite3


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


class HandlerRequestGetResource(HandlerRequestGetData, ABC):
	"""Обработчик запроса на получение одного ресурса"""

	_id: int

	def __init__(self, id):
		super().__init__()
		self._id = id

	def _get_orm_model(self, cls_model: type[db.Model]) -> db.Model:
		"""Получает ORM модель."""
		model = cls_model.query.get(self._id)
		if model is None:
			self._set_error_in_handler_result(
				source=f"/{self._id}",
				error=Errors.NOT_FOUND_PATH
			)
			raise HandlerError
		return model


class HandlerRequestGetAllResources(HandlerRequestGetData, ABC):
	"""Обработчик запроса на получение много ресурсов"""

	def __init__(self):
		super().__init__()

	def _get_orm_models(self, cls_model: type[db.Model]) -> list[db.Model]:
		"""Получает ORM модели."""
		return cls_model.query.all()


class HandlerRequestGetAllResourcesUsingFilter(HandlerRequestGetData, ABC):
	"""Обработчик запроса на получение много ресурсов используя фильтр"""

	_query_string: str | None

	def __init__(self, query_string):
		super().__init__()
		self._query_string = query_string

	def _get_orm_models(self, cls_model: type[db.Model]) -> list[db.Model]:
		"""Получает ORM модели."""
		if self._query_string is None:
			return cls_model.query.all()
		fields = self._get_fields_query()
		parser = QueryStringParser(string=self._query_string, fields=fields)
		try:
			models = GetterModelsUsingCustomFilter(cls_model, parser).get()
		except ErrorQueryStringParsing as e:
			self._set_error_in_handler_result(
				source=e.source,
				error=Errors.FILTER_ERROR
			)
			raise HandlerError
		return models

	@abstractmethod
	def _get_fields_query(self) -> list[FieldQuery]:
		"""Получает поля запроса."""
		raise NotImplementedError()


class HandlerRequestAddData(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса на добавление данных"""

	_data_from_request: dict

	def __init__(self, data_from_request):
		super().__init__()
		self._data_from_request = data_from_request

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на получение данных."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			self._handler_result.document = self._create_document()
		except HandlerError:
			return self._handler_result
		self._handler_result.status_code = 201
		return self._handler_result

	@abstractmethod
	def _create_document(self) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()

	def _get_model_data_post_request(self, model: type[BaseModel]) -> BaseModel:
		"""Получает модель данных POST запроса."""
		try:
			model_data = model(**self._data_from_request)
		except ValidationError as e:
			self._set_error_in_handler_result(
				source=(
			f"Не удалось прочитать: {[fields['loc'] for fields in e.errors()]}"
				),
				error=Errors.BAD_REQUEST
			)
			raise HandlerError
		return model_data

	def _add_record_to_db(self, data: Mapping[str, Any], db_func: Callable)->int:
		"""Добавляет запись в базу данных. Возвращает id записи."""
		try:
			id_record = db_func(data)
		except sqlite3.IntegrityError:
			self._set_error_in_handler_result(
				source="ID не найдены",
				error=Errors.BAD_REQUEST
			)
			raise HandlerError
		return id_record
