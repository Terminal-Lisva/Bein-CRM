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


class HandlerError(Exception):
	pass


class HandlerRequestGetResource(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса на получение ресурса"""

	_id: int
	_cls_orm_model: type[db.Model]

	def __init__(self, id, cls_orm_model):
		super().__init__()
		self._id = id
		self._cls_orm_model = cls_orm_model

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на получение ресурса."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			orm_model = self._get_orm_model()
			self._handler_result.document = self._create_document(orm_model)
		except HandlerError:
			return self._handler_result
		self._handler_result.status_code = 200
		return self._handler_result

	def _get_orm_model(self) -> db.Model:
		"""Получает ORM модель."""
		model = self._cls_orm_model.query.get(self._id)
		if model is None:
			self._set_error_in_handler_result(
				source=f"/{self._id}",
				error=Errors.NOT_FOUND_PATH
			)
			raise HandlerError
		return model

	@abstractmethod
	def _create_document(self, orm_model: db.Model) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()


class HandlerRequestGetResources(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса на получение ресурсов"""

	def __init__(self):
		super().__init__()

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на получение ресурсов."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			orm_models = self._get_orm_models()
			self._handler_result.document = self._create_document(orm_models)
		except HandlerError:
			return self._handler_result
		self._handler_result.status_code = 200
		return self._handler_result

	@abstractmethod
	def _get_orm_models(self) -> list[db.Model]:
		"""Получает ORM модели."""
		raise NotImplementedError()

	@abstractmethod
	def _create_document(self, orm_models: list[db.Model]) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()


class HandlerRequestGetAllResources(HandlerRequestGetResources, ABC):
	"""Обработчик запроса на получение много ресурсов"""

	_cls_orm_model: type[db.Model]

	def __init__(self, cls_orm_model):
		super().__init__()
		self._cls_orm_model = cls_orm_model

	def _get_orm_models(self) -> list[db.Model]:
		"""Получает ORM модели."""
		return self._cls_orm_model.query.all()


class HandlerRequestGetAllResourcesUsingFilter(HandlerRequestGetResources, ABC):
	"""Обработчик запроса на получение много ресурсов используя фильтр"""

	_query_string: str | None
	_cls_orm_model: type[db.Model]

	def __init__(self, query_string, cls_orm_model):
		super().__init__()
		self._query_string = query_string
		self._cls_orm_model = cls_orm_model

	def _get_orm_models(self) -> list[db.Model]:
		"""Получает ORM модели."""
		if self._query_string is None:
			return self._cls_orm_model.query.all()
		fields = self._get_fields_query()
		parser = QueryStringParser(string=self._query_string, fields=fields)
		try:
			models = GetterModelsUsingCustomFilter(
				self._cls_orm_model, parser).get()
		except ErrorQueryStringParsing as e:
			self._set_error_in_handler_result(
				source=e.source,
				error=Errors.FILTER_ERROR
			)
			raise HandlerError
		return models

	@abstractmethod
	def _get_fields_query(self) -> list[FieldQuery]:
		"""Получает запрашиваемые поля."""
		raise NotImplementedError()


class HandlerPostRequest(HandlerRequestWithAuthentication, ABC):
	"""Обработчик POST запроса"""

	_data_from_request: dict
	_model: type[BaseModel]

	def __init__(self, data_from_request, model):
		super().__init__()
		self._data_from_request = data_from_request
		self._model = model

	def _get_model_data_post_request(self) -> BaseModel:
		"""Получает модель данных POST запроса."""
		try:
			model_data = self._model(**self._data_from_request)
		except ValidationError as e:
			self._set_error_in_handler_result(
				source=(
			f"Не удалось прочитать: {[fields['loc'] for fields in e.errors()]}"
				),
				error=Errors.BAD_REQUEST
			)
			raise HandlerError
		return model_data


class HandlerRequestAddData(HandlerPostRequest, ABC):
	"""Обработчик запроса на добавление данных"""

	def __init__(self, data_from_request, model):
		super().__init__(data_from_request, model)

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на добавление данных."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			model_data = self._get_model_data_post_request()
			id = self._add_record_to_db(model_data)
		except HandlerError:
			return self._handler_result
		self._handler_result.document = self._create_document(model_data, id)
		self._handler_result.status_code = 201
		return self._handler_result

	@abstractmethod
	def _add_record_to_db(self, model_data: BaseModel) -> int:
		"""Добавляет запись в базу данных. Возвращает id записи."""
		raise NotImplementedError()

	@abstractmethod
	def _create_document(
		self, model_data: BaseModel, id: int) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()


class HandlerRequestChangeData(HandlerPostRequest, ABC):
	"""Обработчик запроса на изменение данных"""

	_id: int
	_cls_orm_model: type[db.Model]

	def __init__(self, data_from_request, model, id, cls_orm_model):
		super().__init__(data_from_request, model)
		self._id = id
		self._cls_orm_model = cls_orm_model

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на изменение данных."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			model_data = self._get_model_data_post_request()
			self._change_record_to_db(model_data)
			orm_model = self._get_orm_model()
		except HandlerError:
			return self._handler_result
		self._handler_result.document = self._create_document(orm_model)
		self._handler_result.status_code = 200
		return self._handler_result

	@abstractmethod
	def _change_record_to_db(self, model_data: BaseModel) -> None:
		"""Изменяет запись в базе данных."""
		raise NotImplementedError()

	def _get_orm_model(self) -> db.Model:
		"""Получает ORM модель. Исключения не должно быть."""
		return self._cls_orm_model.query.get(self._id)

	@abstractmethod
	def _create_document(self, orm_model: db.Model) -> Mapping[str, Any]:
		"""Создает документ."""
		raise NotImplementedError()


class HandlerRequestDelData(HandlerRequestWithAuthentication, ABC):
	"""Обработчик запроса на удаление данных"""

	_id: int
	_cls_orm_model: type[db.Model]

	def __init__(self, id, cls_orm_model):
		super().__init__()
		self._id = id
		self._cls_orm_model = cls_orm_model

	def handle(self) -> HandlerResult:
		"""Обрабатывает запрос на получение данных."""
		if not self._check_authentication_user():
			return self._handler_result
		try:
			self._make_appeal_to_db()
		except HandlerError:
			return self._handler_result
		self._handler_result.document = {}
		self._handler_result.status_code = 204
		return self._handler_result

	def _get_orm_model(self) -> db.Model:
		"""Получает модель."""
		orm_model = self._cls_orm_model.query.get(self._id)
		if orm_model is None:
			self._set_error_in_handler_result(
				source=f"/{self._id}",
				error=Errors.NOT_FOUND_PATH
			)
			raise HandlerError
		return orm_model

	@abstractmethod
	def _make_appeal_to_db(self) -> None:
		"""Делает обращение к БД."""
		raise NotImplementedError()
