from pydantic import BaseModel, validator, ValidationError
from datetime import date
from typing import TypedDict
from .handler import HandlerRequestGetData, HandlerError
from controller.api.errors import Errors
from controller.api import post_req_parser


class ModelFieldMeta(BaseModel):
    href: str
    type: str

class ModelField(BaseModel):
    meta: ModelFieldMeta

class ModelDoc(BaseModel):
    code_doc: ModelField
    name: str
    date_start: date
    date_finish: date
    responsible: ModelField

    @validator('code_doc')
    def check_type_meta_code_doc(cls, code_doc):
        if code_doc.meta.type != "document management system":
            raise ValueError()
        return code_doc

    @validator('responsible')
    def check_type_meta_responsible(cls, responsible):
        if responsible.meta.type != "app users":
            raise ValueError()
        return responsible


class Meta(TypedDict):
    href: str
    type: str

class DocumentDoc(TypedDict):
    meta: Meta
    id: int
    code_doc: Meta
    name: str
    date_start: date
    date_finish: date
    responsible: Meta
    version: int
    status: int


class HandlerRequestAddDoc(HandlerRequestGetData):
    """Обработчик запроса на добавление документа"""

    _data_from_request: dict

    def __init__(self, data_from_request):
        super().__init__()
        self._data_from_request = data_from_request

    def _create_document(self) -> DocumentDoc:
        """Создает документ."""
        model = self._get_model_post_request()
        ids = self._get_ids_from_model(model)
        id_doc = self._add_doc_to_db(ids)

    def _get_model_post_request(self) -> ModelDoc:
        """Получает модель POST запроса."""
        try:
            model = ModelDoc(**self._data_from_request)
        except ValidationError as e:
            self._set_error_in_handler_result(
                source=(
            f"Не удалось прочитать: {[fields['loc'] for fields in e.errors()]}"
                ),
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return model

    def _get_ids_from_model(self, model: ModelDoc) -> tuple[int, int]:
        """Получает id-ки из модели."""
        try:
            id_code_doc = post_req_parser.get_id(
                path='/docs/code',
                href=model.code_doc.meta.href
            )
            id_responsible = post_req_parser.get_id(
                path='/users',
                href=model.responsible.meta.href
            )
        except post_req_parser.ErrorGettingID as e:
            self._set_error_in_handler_result(
                source= e.source,
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id_code_doc, id_responsible

    def _add_doc_to_db(self, ids: tuple[int, int]) -> int:
        """Добавляет документ в базу данных. Возвращает id документа."""
        id_code_doc, id_responsible = ids
        data = db_docs.DataForAdd(
            id_bpm=id_bpm,
            id_type_doc=id_type_doc,
            id_company=id_company,
            id_creator=self._authentication_user.user_id
        )
        try:
            id_code_doc = db_docs.add_code_doc(data)
        except db_docs.ErrorAddingCodeDoc:
            self._set_error_in_handler_result(
                source="ID не найдены",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id_code_doc
