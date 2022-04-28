from typing import *
from main_objects.registrator import Registrator
from utilities.enums import Errors
from utilities.other import ErrorResponse, SuccessResponse
from flask import request, jsonify, typing


class UserRegistrationPage:
	"""Страница регистрации пользователя"""

	def __init__(self):
		self.__registrator = Registrator()
		self.__error_response = ErrorResponse(Errors.auth)
		self.__success_response = SuccessResponse()
	
	def get_response_data_for_user_registration(self) -> typing.ResponseReturnValue:
		"""Получает ответ - данные для регистрации пользователя"""
		try:
			request_data = request.get_json(force=True, silent=True)
			invitation_token = request_data.get("invitation_token", "")
		except Exception:
			invitation_token = ""
		data_for_user_registration = self.__registrator.forms_data_for_user_registration(invitation_token)
		error_code = data_for_user_registration["error_code"]
		data = data_for_user_registration["data"]
		if error_code is not None:
			return jsonify(self.__error_response.create_response(error_code))
		return jsonify(self.__success_response.create_response(value=data))
	
	def get_response_about_user_registration(self) -> typing.ResponseReturnValue:
		"""Получает ответ о регистрации пользователя"""
		try:
			request_data = request.get_json(force=True, silent=True)
			invitation_token = request_data.get("invitation_token", "")
			password = request_data.get("password", "")
		except Exception:
			invitation_token = ""
			password = ""
		response_about_user_registration = self.__registrator.registers_user(invitation_token, password)
		error_code = response_about_user_registration["error_code"]
		if error_code is not None:
			return jsonify(self.__error_response.create_response(error_code))
		return jsonify(self.__success_response.create_response(
			value="Вы успешно зарегистрировались!"
		))