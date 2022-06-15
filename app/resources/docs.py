from flask_restful import Resource
from flask import typing as flaskTyping
from controller import common
from controller.api.handlers.type_doc import HandlerRequestGetAllTypesDocs
from controller.api.response import Response
from controller.api.handlers.code_doc import HandlerRequestAddCodeDoc


class AllTypesDocs(Resource):

    def get(self) -> flaskTyping.ResponseReturnValue:
        handler = HandlerRequestGetAllTypesDocs()
        return Response(handler).get()


class AllCodesDocs(Resource):
    def post(self) -> flaskTyping.ResponseReturnValue:
        data_from_request = common.get_data_from_request_in_json()
        handler = HandlerRequestAddCodeDoc(data_from_request)
        return Response(handler).get()
