from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller.api.handlers.company import (HandlerRequestGetAllCompany,
HandlerRequestGetCompany)
from controller.api.response import Response


class AllCompany(Resource):

	def get(self) -> flaskTyping.ResponseReturnValue:
		handler = HandlerRequestGetAllCompany()
		return Response(handler).get()


class Company(Resource):

	def get(self, company_id: int) -> flaskTyping.ResponseReturnValue:
		handler = HandlerRequestGetCompany(company_id)
		return Response(handler).get()
