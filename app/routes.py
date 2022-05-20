from app import app
from flask import request, typing as flaskTyping
from pages.page_funcs import get_request_data, error_response, make_success_response, delete_cookies
from pages.response_from_page import ResponseFromPage
from pages.handlers_registration_page import HandlerRequestToGetUserDataForRegistration, HandlerRequestUserRegistration, HandlerRequestUserRestore
from pages.user_authorization_page import UserAuthorizationPage
from pages.page import ConstructorPageTemplateWithSideMenu, PageAvailable, PageWithPermitView


#Страница авторизации/регистрации/восстановления пароля:
@app.route("/data_for_user_registration", methods=["POST"])
def get_data_for_user_registration() -> flaskTyping.ResponseReturnValue:
	"""Получает данные для регистрации пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token"])
		handler = HandlerRequestToGetUserDataForRegistration
		return ResponseFromPage(handler, request_data).get()
	return error_response(code_error=1, type_error="app")

@app.route("/user_registration", methods=["POST"])
def registers_user() -> flaskTyping.ResponseReturnValue:
	"""Регистрирует пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token", "password"])
		handler = HandlerRequestUserRegistration
		return ResponseFromPage(handler, request_data).get()
	return error_response(code_error=1, type_error="app")

@app.route("/restore_user_password", methods=["POST"])
def restores_user_password() -> flaskTyping.ResponseReturnValue:
	"""Восстанавливает пароль пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token", "user_name", "new_password"])
		handler = HandlerRequestUserRestore
		return ResponseFromPage(handler, request_data).get()
	return error_response(code_error=1, type_error="app")

@app.route("/", methods=["GET", "POST"])
def authorizes_user() -> flaskTyping.ResponseReturnValue:
	"""Авторизирует пользователя."""
	if request.method in ["GET", "POST"]:
		return UserAuthorizationPage().get_response_about_user_authorization()
	return error_response(code_error=1, type_error="app")

#Главная страница:
@app.route("/app", methods=["GET"])
def get_app_page() -> flaskTyping.ResponseReturnValue:
	"""Получает главную страницу приложения."""
	if request.method == "GET":
		constructor = ConstructorPageTemplateWithSideMenu("app_page.html")
		return PageAvailable(constructor).get_response_page()
	return error_response(code_error=1, type_error="app")

@app.route("/remove_user_authorization", methods=["DELETE"])
def removes_user_authorization() -> flaskTyping.ResponseReturnValue:
	"""Удаляет авторизацию пользователя."""
	if request.method == "DELETE":
		response = make_success_response(value=True)
		delete_cookies(response)
		return response
	return error_response(code_error=1, type_error="app")

#Страница пользователя:
@app.route("/app/account", methods=["GET"])
def get_account_page() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу приложения."""
	if request.method == "GET":
		constructor = ConstructorPageTemplateWithSideMenu("account_page.html")
		return PageAvailable(constructor).get_response_page()
	return error_response(code_error=1, type_error="app")