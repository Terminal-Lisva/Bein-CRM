from .handler import HandlerRequest
from typing import Optional, TypeVar, Type, Dict
from flask import typing as flaskTyping
from .page_funcs import success_response, error_response


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
			code_error, type_error = handler.get_operation_error()
			return error_response(code_error, type_error)
		return success_response(value=response)