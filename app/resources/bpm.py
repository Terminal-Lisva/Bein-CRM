from flask_restful import Resource, reqparse
from flask import typing as flaskTyping
from controller.api.handlers.bpm import HandlerRequestGetAllBpm
from controller.api.response import Response


parser_bpm = reqparse.RequestParser()
parser_bpm.add_argument("filter", type=str, location='args')

class AllBpm(Resource):

    def get(self) -> flaskTyping.ResponseReturnValue:
        query_string = parser_bpm.parse_args()["filter"]
        handler = HandlerRequestGetAllBpm(query_string)
        return Response(handler).get()
