from flask_restful import Resource, reqparse
from flask import typing as flaskTyping


class Company(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		
