from app import app
from flask import request, typing as flaskTyping
from pages.page_funcs import (redirect_response, error_response,
delete_cookies, template_response, make_success_response,
get_data_from_json, get_data_from_url)
from pages.authorization_page import AuthPage
from pages.response import Response
from pages.handlers_registration_page import (
HandlerRequestToGetUserDataForRegistration,HandlerRequestUserRegistration,
HandlerRequestUserRestore)
from pages.page import (ConstructorPageTemplateWithSideMenu,
PageAvailable, PageWithPermitView)
from pages.handler_account_page import HandlerRequestChangePassword


#Корневая страница:
@app.route("/", methods=["GET"])
def root() -> flaskTyping.ResponseReturnValue:
	"""Корневой route (оставил на будующий контент)."""
	if request.method == "GET":
		return redirect_response(to="/session/new")
	return error_response(
		source_error="/", type_error="REQUEST_METHOD", code_error=1)

#Страница авторизации пользователя
@app.route("/session/new", methods=["GET"])
def get_auth_page() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу авторизации."""
	if request.method == "GET":
		return template_response(template="auth_page.html")
	return error_response(
		source_error="/session/new", type_error="REQUEST_METHOD", code_error=1)

#Аутентификация пользователя
@app.route("/session", methods=["POST", "DELETE"])
def authenticates_user() -> flaskTyping.ResponseReturnValue:
	"""Аутентифицирует пользователя."""
	if request.method == "POST":
		return AuthPage().get_response_about_user_authentication()
	elif request.method == "DELETE":
		response = make_success_response(response={}, status_code=201)
		delete_cookies(response)
		return response
	return error_response(
		source_error="/session", type_error="REQUEST_METHOD", code_error=1)

#@app.route("/users/new", methods=["GET"])
#Страница регистрации пользователя строится JS на странице авторизации

#Клиенту API нужно подтверждение от сервера для регистрации!
@app.route("/users/new/proof", methods=["GET"])
def get_data_for_user_registration() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу регистрации пользователя."""
	if request.method == "GET":
		request_data = get_data_from_url(args=["invitation_token"])
		handler = HandlerRequestToGetUserDataForRegistration
		return Response(request_data, handler, status_code=200).get()
	return error_response(
	source_error="/users/new/proof", type_error="REQUEST_METHOD", code_error=1)

#Регистрация пользователя
@app.route("/users", methods=["POST"])
def registers_user() -> flaskTyping.ResponseReturnValue:
	if request.method == "POST":
		request_data = get_data_from_json(keys=["invitation_token", "password"])
		handler = HandlerRequestUserRegistration
		return Response(request_data, handler, status_code=201).get()
	#GET user можем реализовать через user.py -> User
	#PATCH на изменение данных пользователя, в том числе пароля
	return error_response(
		source_error="/users", type_error="REQUEST_METHOD", code_error=1)

#Восстановление пароля пользователя
@app.route("/users/password", methods=["PUT"])
def restores_user_password() -> flaskTyping.ResponseReturnValue:
	"""Восстановление пароля пользователя."""
	if request.method == "PUT":
		request_data = get_data_from_json(
			keys=["invitation_token", "user_name", "new_password"])
		handler = HandlerRequestUserRestore
		return Response(request_data, handler, status_code=201).get()
	return error_response(
	source_error="/users/password", type_error="REQUEST_METHOD", code_error=1)

#Главная страница приложения:
@app.route("/app", methods=["GET"])
def get_app_page() -> flaskTyping.ResponseReturnValue:
	"""Получает главную страницу приложения."""
	if request.method == "GET":
		constructor = ConstructorPageTemplateWithSideMenu("app_page.html")
		return PageAvailable(constructor).get_response_page()
	return error_response(
		source_error="/app", type_error="REQUEST_METHOD", code_error=1)

#Страница пользователя в приложении:
@app.route("/app/account", methods=["GET"])
def get_account_page() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу аккаунта в приложении."""
	if request.method == "GET":
		constructor = ConstructorPageTemplateWithSideMenu("account_page.html")
		return PageAvailable(constructor).get_response_page()
	return error_response(
		source_error="/app/account", type_error="REQUEST_METHOD", code_error=1)

#@app.route("/app/account/change_password", methods=["PUT"])
#def change_password() -> flaskTyping.ResponseReturnValue:
#	"""Изменяет пароль."""
#	if request.method == "PUT":
#		request_data = get_data_from_json(["password", "new_password"])
#		handler = HandlerRequestChangePassword
#		return Response(handler, request_data).get()
#	return error_response(code_error=1, type_error="app")
