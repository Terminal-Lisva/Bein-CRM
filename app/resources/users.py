from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller.api.handler_users import (HandlerRequestGetUsers,
HandlerRequestAddUser, HandlerRequestUsersPassword)
from controller.api.response import Response


#args for get user:
parser_get_user = reqparse.RequestParser()
parser_get_user.add_argument("invitation_token", type=str, location='args')
#args for post user:
parser_post_user = reqparse.RequestParser()
parser_post_user.add_argument("invitation_token", type=str, required=True)
parser_post_user.add_argument("password", type=str, required=True)

class Users(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		token = parser_get_user.parse_args()["invitation_token"]
		handler = HandlerRequestGetUsers(token)
		return Response(handler, status_code=200).get()

	def post(self) -> flaskTyping.ResponseReturnValue:
		token = parser_post_user.parse_args()["invitation_token"]
		password = parser_post_user.parse_args()["password"]
		handler = HandlerRequestAddUser(token, password)
		return Response(handler, status_code=201).get()


#args for put password user:
parser_put_password_user = reqparse.RequestParser()
parser_put_password_user.add_argument("invitation_token",type=str,required=True)
parser_put_password_user.add_argument("new_password",type=str,required=True)

class UsersPassword(Resource):

	def put(self) -> flaskTyping.ResponseReturnValue:
		token = parser_put_password_user.parse_args()["invitation_token"]
		password = parser_put_password_user.parse_args()["new_password"]
		handler = HandlerRequestUsersPassword(token, password)
		return Response(handler, status_code=201).get()
