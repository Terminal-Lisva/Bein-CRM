from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller.api.handlers_account_access import (HandlerRequestAddAccount,
HandlerRequestRestoreAccount)
from controller.api.response import Response


#args for post user:
parser_users = reqparse.RequestParser()
parser_users.add_argument("invitation_token", type=str, required=True)
parser_users.add_argument("password", type=str, required=True)

class Users(Resource):

	def post(self) -> flaskTyping.ResponseReturnValue:
		token = parser_users.parse_args()["invitation_token"]
		password = parser_users.parse_args()["password"]
		handler = HandlerRequestAddAccount(token, password)
		return Response(handler, status_code=201).get()


#args for put password user:
parser_users_password = reqparse.RequestParser()
parser_users_password.add_argument("invitation_token",type=str,required=True)
parser_users_password.add_argument("new_password",type=str,required=True)

class UsersPassword(Resource):

	def put(self) -> flaskTyping.ResponseReturnValue:
		token = parser_users_password.parse_args()["invitation_token"]
		password = parser_users_password.parse_args()["new_password"]
		handler = HandlerRequestRestoreAccount(token, password)
		return Response(handler, status_code=201).get()
