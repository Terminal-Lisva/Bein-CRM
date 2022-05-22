from .handler import HandlerRequest
from typing import Type, Optional, Dict
from flask import typing as flaskTyping
from .page_funcs import success_response, error_response


class Response:
	"""Ответ"""

	__request_data: Optional[Dict[str, str]]
	__handler: Type[HandlerRequest]
	__status_code: int

	def __init__(self, request_data, handler, status_code):
		self.__handler = handler
		self.__request_data = request_data
		self.__status_code = status_code

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		if self.__request_data is None:
			return error_response(
				source_error='request data',
				type_error='REQUEST_DATA',
				code_error=1)
		handler = self.__handler(self.__request_data)
		response = handler.handle()
		if not response:
			source_error, type_error, code_error = handler.get_operation_error()
			return error_response(source_error, type_error, code_error)
		return success_response(response, self.__status_code)
