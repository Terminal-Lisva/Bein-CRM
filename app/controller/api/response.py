from .handler import HandlerRequest, ExcHandlerError
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
		except ExcHandlerError:
			result = False
		if not result:
			error = self.__handler.get_handler_error()
			return common.error_response(
				source_error=error.source,
				type_error=error.type,
				code_error=error.code
			)
		return common.make_json_response(result.document, result.status_code)
