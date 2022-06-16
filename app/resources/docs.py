from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller import common
from controller.api.handlers.type_doc import HandlerRequestGetAllTypesDocs
from controller.api.response import Response
from controller.api.handlers.code_doc import (HandlerRequestAddCodeDoc,
HandlerRequestDelCodeDoc, HandlerRequestGetAllCodeDocs)


class AllTypesDocs(Resource):

    def get(self) -> flaskTyping.ResponseReturnValue:
        handler = HandlerRequestGetAllTypesDocs()
        return Response(handler).get()


parser_code_doc = reqparse.RequestParser()
parser_code_doc.add_argument("filter", type=str, location='args')

class AllCodesDocs(Resource):

    def post(self) -> flaskTyping.ResponseReturnValue:
        data_from_request = common.get_data_from_request_in_json()
        handler = HandlerRequestAddCodeDoc(data_from_request)
        return Response(handler).get()

    def get(self) -> flaskTyping.ResponseReturnValue:
        query_string = parser_code_doc.parse_args()["filter"]
        handler = HandlerRequestGetAllCodeDocs(query_string)
        return Response(handler).get()


class CodeDoc(Resource):

    def delete(self, id_code_doc: int) -> flaskTyping.ResponseReturnValue:
        handler = HandlerRequestDelCodeDoc(id_code_doc)
        return Response(handler).get()
