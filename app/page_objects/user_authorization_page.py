from typing import *
from main_objects.authenticator import Authenticator
from main_objects.registrator import Registrator
from utilities.enums import Errors
from utilities.other import ErrorResponse, SuccessResponse
from flask import request, render_template, make_response, redirect, jsonify, typing


class UserAuthorizationPage:
	"""Страница авторизации пользователя"""

	def __init__(self):
		self.__authenticator = Authenticator()
		self.__error_response = ErrorResponse(Errors.auth)
		self.__success_response = SuccessResponse()
	
	def get_response_about_user_authorization(self) -> typing.ResponseReturnValue:
		"""Получает ответ об авторизации пользователя"""
		try:
			request_data = request.get_json(force=True, silent=True)
			email = request_data.get("email", None)
			password = request_data.get("password", None)
		except Exception:
			email = None
			password = None
		info_user_authentication = self.__authenticator.authenticates_user(email, password)
		error_code = info_user_authentication["error_code"]
		if error_code is not None:
			return jsonify(self.__error_response.create_response(error_code))
		user_id = info_user_authentication["user_id"]
		if user_id is None:
			return render_template('user_auth_page.html')
		response = make_response(redirect('/app'))
		cookie_session = info_user_authentication["cookie_session"]
		if cookie_session is not None:
			response.set_cookie(key='Session', value=cookie_session, httponly=True)
		cookie_auth = info_user_authentication["cookie_auth"]
		if cookie_auth is not None:
			response.set_cookie(key='Auth', value=cookie_auth, max_age=60*60*24*30, httponly=True)
		return response
	
	def get_response_about_remove_authorization(self) -> typing.ResponseReturnValue:
		"""Получает ответ об удалении авторизации"""
		response = make_response(jsonify(self.__success_response.create_response(value=True)))
		response.delete_cookie('Session')
		response.delete_cookie('Auth')
		return response

	def get_response_about_restore_password(self) -> typing.ResponseReturnValue:
		"""Получает ответ о восстановлении пароля"""
		try:
			request_data = request.get_json(force=True, silent=True)
			invitation_token = request_data.get("invitation_token", "")
			user_name = request_data.get("user_name", "")
			password = request_data.get("password", "")
		except Exception:
			invitation_token = ""
			user_name = ""
			password = ""
		response_about_restore_password = Registrator().restores_password(invitation_token, user_name, password)
		error_code = response_about_restore_password["error_code"]
		if error_code is not None:
			return jsonify(self.__error_response.create_response(error_code))
		return jsonify(self.__success_response.create_response(
			value="Пароль успешно восстановлен!"
		))