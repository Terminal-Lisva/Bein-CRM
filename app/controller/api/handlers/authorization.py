from abc import ABC, abstractmethod
from flask import typing as flaskTyping
from controller.service_layer.authentication import (Authentication,
AuthenticationByEmailAndPassword, AuthenticationByCookieSession,
AuthenticationByCookieAuth)
from controller import common
from controller.api.errors import Errors
from itertools import filterfalse


class ResponseHandler(ABC):
	"""Базовый класс для обработчиков ответа"""

	_response: flaskTyping.ResponseReturnValue | None = None

	def __init__(self, successor = None):
		self.__successor = successor

	def handle(self) -> None:
		"""Обрабатывает."""
		result = self._check_request()
		if not result:
			self.__successor.handle()

	@abstractmethod
	def _check_request(self) -> bool:
		"""Проверяет запрос."""
		raise NotImplementedError()

	@property
	def response(self) -> flaskTyping.ResponseReturnValue | None:
		return self._response


class EmailAndPasswordHandler(ResponseHandler):
	"""Обработчик емайла и пароля"""

	def __init__(self, successor: ResponseHandler | None = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		data_from_request = common.get_data_from_request_in_json()
		try:
			email = str(data_from_request["email"])
			password = str(data_from_request["password"])
		except (TypeError, KeyError):
			return False
		authentication = AuthenticationByEmailAndPassword(email, password)
		user_id = authentication.authenticates_user()
		if user_id is not None:
			self._response = common.make_json_response(
				response={"message": "Сессия успешно установлена"},
				status_code=201
			)
			common.add_cookies_to_response(
				self._response,
				cookie_session=authentication.get_cookie_session(),
				cookie_auth=authentication.get_cookie_auth()
			)
		else:
			error = authentication.get_operation_error()
			message, status_code = error.value
			response = {
				"source": error.source,
				"type": error.name,
				"message": message
			}
			self._response = common.make_json_response(response, status_code)
		return True


class CookieSessionHandler(ResponseHandler):
	"""Обработчик куки сессии"""

	def __init__(self, successor: ResponseHandler | None = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_session = common.get_cookie("Session")
		authentication = AuthenticationByCookieSession(cookie_session)
		user_id = authentication.authenticates_user()
		if user_id is None:
			return False
		self._response = common.make_json_response(
			response={"message": "Сессия успешно установлена"},
			status_code=201
		)
		return True


class CookieAuthHandler(ResponseHandler):
	"""Обработчик куки авторизации"""

	def __init__(self, successor: ResponseHandler | None = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_auth = common.get_cookie("Auth")
		authentication = AuthenticationByCookieAuth(cookie_auth)
		user_id = authentication.authenticates_user()
		if user_id is None:
			return False
		self._response = common.make_json_response(
			response={"message": "Сессия успешно установлена"},
			status_code=201
		)
		common.add_cookies_to_response(
			self._response,
			cookie_session=authentication.get_cookie_session()
		)
		return True


class LastHandler(ResponseHandler):
	"""Обработчик последний"""

	def __init__(self, successor: ResponseHandler | None = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		message, status_code = Errors.NO_AUTHENTICATION.value
		response = {
			"source": "cookies",
			"type": Errors.NO_AUTHENTICATION.name,
			"message": message
		}
		self._response = common.make_json_response(response, status_code)
		return True


class Authorization:
	"""Авторизации пользователя"""

	def response_about_user_session(
		self) -> flaskTyping.ResponseReturnValue:
		"""Ответ о сессии пользователя."""
		last_handler = LastHandler()
		cookie_auth_handler = CookieAuthHandler(last_handler)
		cookie_session_handler = CookieSessionHandler(cookie_auth_handler)
		email_password_handler = EmailAndPasswordHandler(cookie_session_handler)
		email_password_handler.handle()
		#Находим ответ из обработчиков
		handlers = [
			last_handler,
			cookie_auth_handler,
			cookie_session_handler,
			email_password_handler,
		]
		for handler in filterfalse(
				lambda handler: handler.response is None,
				handlers):
			return handler.response
