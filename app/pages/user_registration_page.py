from flask import typing as flaskTyping
from typing import Optional, Dict
from service_layer.user_registration import Registration, UserDataForRegistration, UserRegistrator, UserRestorer
from .page_funcs import get_request_data, success_response, error_response


class UserRegistrationPage:
	"""Страница регистрации пользователя"""
	
	def get_response_data_for_user_registration(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ - данные для регистрации пользователя."""
		request_data = get_request_data(["invitation_token"])
		response = self.__forms_response(request_data, UserDataForRegistration)
		return response
	
	def get_response_about_user_registration(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ о регистрации пользователя."""
		request_data = get_request_data(["invitation_token", "password"])
		response = self.__forms_response(request_data, UserRegistrator)
		return response
	
	def get_response_about_restore_password(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ о восстановлении пароля."""
		request_data = get_request_data(["invitation_token", "user_name", "new_password"])
		response = self.__forms_response(request_data, UserRestorer)
		return response

	def __forms_response(self, request_data: Optional[Dict[str, str]], registration: Registration):
		"""Формирует ответ пользователю."""
		if request_data is None:
			return error_response(code_error=2, type_error="app")
		init_registration = registration(request_data)
		response = init_registration.get_response()
		if not response:
			code_error = init_registration.get_operation_error()
			return error_response(code_error, type_error="auth")
		return success_response(value=response)
	