from typing import *
from flask import request, typing
from app import app
from utilities.other import get_error_http
from page_objects.user_registration_page import UserRegistrationPage
from page_objects.user_authorization_page import UserAuthorizationPage


@app.route("/data_for_user_registration", methods=["POST"])
def get_data_for_user_registration() -> typing.ResponseReturnValue:
	"""Получает данные для регистрации пользователя"""
	if request.method == "POST":
		return UserRegistrationPage().get_response_data_for_user_registration()
	return get_error_http()

@app.route("/user_registration", methods=["POST"])
def registers_user() -> typing.ResponseReturnValue:
	"""Регистрирует пользователя"""
	if request.method == "POST":
		return UserRegistrationPage().get_response_about_user_registration()
	return get_error_http()

@app.route("/", methods=["GET", "POST"])
def authorizes_user() -> typing.ResponseReturnValue:
	"""Авторизирует пользователя"""
	if request.method == "GET" or request.method == "POST":
		return UserAuthorizationPage().get_response_about_user_authorization()
	return get_error_http()

@app.route("/remove_user_authorization", methods=["POST"])
def removes_user_authorization() -> typing.ResponseReturnValue:
	"""Удаляет авторизацию пользователя"""
	if request.method == "POST":
		return UserAuthorizationPage().get_response_about_remove_authorization()
	return get_error_http()

@app.route("/restore_user_password", methods=["POST"])
def restores_user_password() -> typing.ResponseReturnValue:
	"""Восстанавливает пароль пользователя"""
	if request.method == "POST":
		return UserAuthorizationPage().get_response_about_restore_password()
	return get_error_http()

@app.route("/app", methods=["GET"])
def show_user_main_page_app() -> typing.ResponseReturnValue:
	"""Показывает пользователю главную страницу приложения"""
	if request.method == "GET":
		return 'Привееет!'