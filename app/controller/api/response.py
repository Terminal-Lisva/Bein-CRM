from abc import ABC, abstractmethod
from .handlers.handler import HandlerRequest
from flask import typing as flaskTyping
from controller import common


class ResponseJSON(ABC):
	"""Ответ в формате JSON"""

	_handler: HandlerRequest

	def __init__(self, handler):
		self._handler = handler

	@abstractmethod
	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		raise NotImplementedError()

	def _make_json_response(self) -> flaskTyping.ResponseReturnValue:
		result = self._handler.handle()

		response = {
			"source": result.error.source,
			"type": result.error.type,
			"message": result.error.message
		} if not result else result.document
		status_code = result.status_code
		return common.make_json_response(response, status_code)


class Response(ResponseJSON):
	"""Ответ"""

	def __init__(self, handler):
		super().__init__(handler)

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		return self._make_json_response()


class ResponseWithAdditionCookie(ResponseJSON):
	"""Ответ с добавлением куки"""

	def __init__(self, handler):
		super().__init__(handler)

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ."""
		response_json = self._make_json_response()
		common.add_cookies_to_response(
			response_json,
			cookie_auth = self._handler.get_cookie_auth()
		)
		return response_json
