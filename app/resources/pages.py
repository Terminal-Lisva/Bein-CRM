from flask_restful import Resource
from flask import typing as flaskTyping
from controller.pages.page import (ConstructorPageTemplateWithSideMenu,
PageAvailable)


class AppPage(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		constructor = ConstructorPageTemplateWithSideMenu("app_page.html")
		return PageAvailable(constructor).get_response_page()

class AccountPage(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		constructor = ConstructorPageTemplateWithSideMenu("account_page.html")
		return PageAvailable(constructor).get_response_page()
