from flask_restful import Resource
from flask import typing as flaskTyping
from controller.pages.page import ConstructorPageTemplateWithSideMenu
from controller.pages.main_page import MainPage
from controller.pages.account_page import AccountPage


class App(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		constructor = ConstructorPageTemplateWithSideMenu("app.html")
		return MainPage(constructor).get_response_page()

class Account(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		constructor = ConstructorPageTemplateWithSideMenu("account.html")
		return AccountPage(constructor).get_response_page()
