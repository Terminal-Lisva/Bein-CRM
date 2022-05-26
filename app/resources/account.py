from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller.api.account_change_password import (
HandlerRequestСhangePassword, ResponseAboutChangePassword)


#args for post user:
parser_account_password = reqparse.RequestParser()
parser_account_password.add_argument("password", type=str, required=True)
parser_account_password.add_argument("new_password", type=str, required=True)

class AccountPassword(Resource):

	def put(self, user_id: int) -> flaskTyping.ResponseReturnValue:
		password = parser_account_password.parse_args()["password"]
		new_password = parser_account_password.parse_args()["new_password"]
		handler = HandlerRequestСhangePassword(user_id, password, new_password)
		return ResponseAboutChangePassword(handler).get()
