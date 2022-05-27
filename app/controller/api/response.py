from .handler import HandlerRequest, HandlerError
from flask import typing as flaskTyping
from controller import common


class Response:
	"""Ответ"""

	__handler: HandlerRequest

	def __init__(self, handler):
		self.__handler = handler

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		try:
			result = self.__handler.handle()
		except HandlerError:
			result = None

		if result is None:
			source_error, type_error, code_error = \
											self.__handler.get_handler_error()
			return common.error_response(source_error, type_error, code_error)
		response, status_code = result
		return common.make_json_response(response, status_code)
