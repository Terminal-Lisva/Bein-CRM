from app import app
from flask import request, typing as flaskTyping
from pages.page_funcs import get_request_data, error_response, delete_cookies
from pages.user_registration_page import UserRegistrationPage, HandlerResponseUserRegistrationData, HandlerResponseAboutUserRegistration, HandlerResponseAboutUserRestore
from pages.user_authorization_page import UserAuthorizationPage
from pages.app_page import AppPage
from pages.account_page import AccountPage


#Страница авторизации/регистрации/восстановления пароля
@app.route("/data_for_user_registration", methods=["POST"])
def get_data_for_user_registration() -> flaskTyping.ResponseReturnValue:
	"""Получает данные для регистрации пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token"])
		user_registration_page = UserRegistrationPage(HandlerResponseUserRegistrationData, request_data)
		return user_registration_page.get_response()
	return error_response(code_error=1, type_error="app")

@app.route("/user_registration", methods=["POST"])
def registers_user() -> flaskTyping.ResponseReturnValue:
	"""Регистрирует пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token", "password"])
		user_registration_page = UserRegistrationPage(HandlerResponseAboutUserRegistration, request_data)
		return user_registration_page.get_response()
	return error_response(code_error=1, type_error="app")

@app.route("/restore_user_password", methods=["POST"])
def restores_user_password() -> flaskTyping.ResponseReturnValue:
	"""Восстанавливает пароль пользователя."""
	if request.method == "POST":
		request_data = get_request_data(["invitation_token", "user_name", "new_password"])
		user_registration_page = UserRegistrationPage(HandlerResponseAboutUserRestore, request_data)
		return user_registration_page.get_response()
	return error_response(code_error=1, type_error="app")

@app.route("/", methods=["GET", "POST"])
def authorizes_user() -> flaskTyping.ResponseReturnValue:
	"""Авторизирует пользователя."""
	if request.method in ["GET", "POST"]:
		return UserAuthorizationPage().get_response_about_user_authorization()
	return error_response(code_error=1, type_error="app")

@app.route("/remove_user_authorization", methods=["DELETE"])
def removes_user_authorization() -> flaskTyping.ResponseReturnValue:
	"""Удаляет авторизацию пользователя."""
	if request.method == "DELETE":
		response = make_success_response(value=True)
		delete_cookies(response)
		return response
	return error_response(code_error=1, type_error="app")

#Главная страница
@app.route("/app", methods=["GET"])
def get_app_page() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу приложения."""
	if request.method == "GET":
		return AppPage().get_response_page()
	return error_response(code_error=1, type_error="app")

#Страница пользователя
@app.route("/app/account", methods=["GET"])
def get_account_page() -> flaskTyping.ResponseReturnValue:
	"""Получает страницу приложения."""
	if request.method == "GET":
		return AccountPage().get_response_page()
	return error_response(code_error=1, type_error="app")