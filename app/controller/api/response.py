from .handler import HandlerRequest, HandlerError
from flask import typing as flaskTyping
from controller import common


class Response:
	"""Ответ"""

	__handler: HandlerRequest
	__status_code: int

	def __init__(self, handler, status_code):
		self.__handler = handler
		self.__status_code = status_code

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		try:
			result = self.__handler.handle()
		except HandlerError:
			result = None
		if not result:
			source_error, type_error, code_error = \
											self.__handler.get_handler_error()
			return common.error_response(source_error, type_error, code_error)
		return common.make_json_response(result, self.__status_code)
