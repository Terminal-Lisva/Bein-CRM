from abc import ABC, abstractmethod
from typing import Optional
from flask import typing as flaskTyping
from service_layer.authentication import (Authentication,
AuthenticationByEmailAndPassword, AuthenticationByCookieSession,
AuthenticationByCookieAuth)
from .page_funcs import (get_data_from_json, get_cookie, make_success_response,
add_cookies_to_response, error_response)
from itertools import filterfalse


class ResponseHandler(ABC):
	"""Базовый класс для обработчиков ответа"""

	_response: Optional[flaskTyping.ResponseReturnValue] = None

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
	def response(self) -> Optional[flaskTyping.ResponseReturnValue]:
		return self._response


class EmailAndPasswordHandler(ResponseHandler):
	"""Обработчик емайла и пароля"""

	def __init__(self, successor: Optional[ResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		request_data = get_data_from_json(keys=["email", "password"])
		if request_data is None:
			return False
		email = request_data["email"]
		password = request_data["password"]
		authentication = AuthenticationByEmailAndPassword(email, password)
		user_id = authentication.authenticates_user()
		if user_id is not None:
			self._response = make_success_response(
				response={"value": True},
				status_code=200
			)
			add_cookies_to_response(
				self._response,
				cookie_session=authentication.get_cookie_session(),
				cookie_auth=authentication.get_cookie_auth()
			)
		else:
			source, type, code = authentication.get_operation_error()
			self._response = error_response(source, type, code)
		return True


class CookieSessionHandler(ResponseHandler):
	"""Обработчик куки сессии"""

	def __init__(self, successor: Optional[ResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_session = get_cookie("Session")
		authentication = AuthenticationByCookieSession(cookie_session)
		user_id = authentication.authenticates_user()
		if user_id is None:
			return False
		self._response = make_success_response(
			response={"value": True},
			status_code=200
		)
		return True


class CookieAuthHandler(ResponseHandler):
	"""Обработчик куки авторизации"""

	def __init__(self, successor: Optional[ResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_auth = get_cookie("Auth")
		authentication = AuthenticationByCookieAuth(cookie_auth)
		user_id = authentication.authenticates_user()
		if user_id is None:
			return False
		self._response = make_success_response(
			response={"value": True},
			status_code=200
		)
		add_cookies_to_response(
			self._response,
			cookie_session=authentication.get_cookie_session()
		)
		return True


class LastHandler(ResponseHandler):
	"""Обработчик последний"""

	def __init__(self, successor: Optional[ResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		self._response = error_response(
			source="cookies", type="REQUEST_AUTH", code=1)
		return True


class AuthPage:
	"""Страница авторизации пользователя"""

	def get_response_about_user_authentication(
		self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ об аутентификации пользователя."""
		last_handler = LastHandler()
		cookie_auth_handler = CookieAuthHandler(last_handler)
		cookie_session_handler = CookieSessionHandler(cookie_auth_handler)
		email_and_password_handler = EmailAndPasswordHandler(
														cookie_session_handler)
		email_and_password_handler.handle()
		#Находим ответ из обработчиков
		handlers = [
			last_handler,
			cookie_auth_handler,
			cookie_session_handler,
			email_and_password_handler,
		]
		for handler in filterfalse(
				lambda handler: handler.response is None,
				handlers):
			return handler.response
