from abc import ABC, abstractmethod
from typing import Optional
from flask import typing as flaskTyping
from main_objects.user_authentication import UserAuthenticationInfo, Authentication, AuthenticationByEmailAndPassword, AuthenticationByCookieSession, AuthenticationByCookieAuth
from .page_funcs import get_request_data, get_cookie, success_response, success_response_with_cookies, error_response, redirect_response, render_template_response, delete_cookies
from itertools import filterfalse


class AuthResponseHandler(ABC):
	"""Базовый класс для обработчиков ответа об авторизации"""
	
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
		raise NotImplementedError()
	
	def _authenticates_user(self, authentication: Authentication) -> UserAuthenticationInfo:
		"""Аутентифицирует пользователя."""
		return authentication.get_user_authentication_info()
	
	@property
	def response(self) -> Optional[flaskTyping.ResponseReturnValue]:
		return self._response


class EmailAndPasswordHandler(AuthResponseHandler):
	"""Обработчик емайла и пароля"""

	def __init__(self, successor: Optional[AuthResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		request_data = get_request_data(["email", "password"])
		if request_data is None:
			return False	
		email = request_data["email"]
		password = request_data["password"]
		authentication = AuthenticationByEmailAndPassword(email, password)
		user_authentication_info = self._authenticates_user(authentication)
		if user_authentication_info:
			self._response = success_response_with_cookies(
				value=True,
				cookie_session=user_authentication_info.cookie_session,
				cookie_auth=user_authentication_info.cookie_auth
			)
		else:
			code_error = authentication.get_operation_error()
			self._response = error_response(code_error, type_error="auth")
		return True


class CookieSessionHandler(AuthResponseHandler):
	"""Обработчик куки сессии"""

	def __init__(self, successor: Optional[AuthResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_session = get_cookie("Session")
		authentication = AuthenticationByCookieSession(cookie_session)
		user_authentication_info = self._authenticates_user(authentication)
		if not user_authentication_info:
			return False
		self._response = redirect_response(
			route="/app"
		)
		return True


class CookieAuthHandler(AuthResponseHandler):
	"""Обработчик куки авторизации"""

	def __init__(self, successor: Optional[AuthResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		cookie_auth = get_cookie("Auth")
		authentication = AuthenticationByCookieAuth(cookie_auth)
		user_authentication_info = self._authenticates_user(authentication)
		if not user_authentication_info:
			return False
		self._response = redirect_response(
			route="/app",
			cookie_session=user_authentication_info.cookie_session
		)
		return True


class LastHandler(AuthResponseHandler):
	"""Обработчик последний"""

	def __init__(self, successor: Optional[AuthResponseHandler] = None):
		super().__init__(successor)

	def _check_request(self) -> bool:
		self._response = render_template_response(
			template_name="user_auth_page.html"
		)
		return True


class UserAuthorizationPage:
	"""Страница авторизации пользователя"""
	
	def get_response_about_user_authorization(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ об авторизации пользователя."""
		last_handler = LastHandler()
		cookie_auth_handler = CookieAuthHandler(last_handler)
		cookie_session_handler = CookieSessionHandler(cookie_auth_handler)
		email_and_password_handler = EmailAndPasswordHandler(cookie_session_handler)
		email_and_password_handler.handle()
		#находим ответ из обработчиков
		handlers = [email_and_password_handler, cookie_session_handler, cookie_auth_handler, last_handler]
		for handler in filterfalse(
				lambda handler: handler.response is None, 
				handlers):
			return handler.response

	def get_response_about_remove_authorization(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ об удалении авторизации."""
		return delete_cookies()