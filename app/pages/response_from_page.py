from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, TypeVar, Type, Dict
from utilities.validations import Validation
from enum import Enum
from flask import typing as flaskTyping
from .page_funcs import success_response, error_response


#Логика получения ответа от страницы:
class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_operation_error: Optional[int]

	def __init__(self):
		self._operation_error = None

	@abstractmethod
	def handle(self) -> Optional[Union[bool, Tuple[str]]]:
		"""Обрабатывает соответствующий запрос."""
		raise NotImplementedError()

	def _check_validation_value(self, value: str, validation: Validation, error_type: Enum):
		"""Проверяет значение на валидацию."""
		if not (result := validation(value).get_result()):
			self._set_operation_error(error_type)
		return result

	def _set_operation_error(self, error_type: Enum) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = error_type.value

	def get_operation_error(self) -> Optional[int]:
		"""Получает ошибку операции."""
		return self._operation_error


Handler = TypeVar("Handler", bound=HandlerRequest)


class ResponseFromPage:
	"""Ответ от страницы"""

	__handler: Type[Handler]
	__request_data: Optional[Dict[str, str]]

	def __init__(self, handler, request_data):
		self.__handler = handler
		self.__request_data = request_data

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ от страницы."""
		if self.__request_data is None:
			return error_response(code_error=2, type_error="app")
		handler = self.__handler(self.__request_data)
		response = handler.handle()
		if not response:
			code_error = handler.get_operation_error()
			return error_response(code_error, type_error="auth")
		return success_response(value=response)