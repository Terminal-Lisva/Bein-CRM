from flask_restful import Resource
from flask import typing as flaskTyping
from controller import common
from controller.api.handlers.user import (HandlerRequestAddUser,
HandlerRequestRestoreUser)
from controller.api.response import Response


class Users(Resource):

	def post(self) -> flaskTyping.ResponseReturnValue:
		data_from_request = common.get_data_from_request_in_json()
		handler = HandlerRequestAddUser(data_from_request)
		return Response(handler).get()


class UsersPassword(Resource):

	def put(self) -> flaskTyping.ResponseReturnValue:
		data_from_request = common.get_data_from_request_in_json()
		handler = HandlerRequestRestoreUser(data_from_request)
		return Response(handler).get()
