from flask_restful import Resource
from flask import typing as flaskTyping
from controller.api.authorization import Authorization
from controller import common


class Session(Resource):

	def post(self) -> flaskTyping.ResponseReturnValue:
		#необязательные аргументы "email"/"password" парсятся внутри объекта
		return Authorization().response_about_user_session()

	def delete(self) -> flaskTyping.ResponseReturnValue:
		response = common.make_json_response({}, 204)
		common.delete_cookies(response)
		return response


class SessionNew(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		return common.template_response(template="authorization.html")
