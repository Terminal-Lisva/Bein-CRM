from pydantic import BaseModel, validator, ValidationError
from typing import TypedDict
from .handler import HandlerRequestGetData, HandlerError
from controller.api.errors import Errors
from controller.api import post_req_parser
from database import db_docs
from database.models.code_doc import CodeDoc
from controller.api import for_api


class ModelFieldMeta(BaseModel):
    href: str
    type: str

class ModelField(BaseModel):
    meta: ModelFieldMeta

class ModelCodeDoc(BaseModel):
    bpm: ModelField
    type_doc: ModelField
    company: ModelField

    @validator('bpm')
    def get_id_from_bpm(cls, bpm):
        if bpm.meta.type != "process management":
            raise ValueError()
        return bpm

    @validator('type_doc')
    def get_id_from_type_doc(cls, type_doc):
        if type_doc.meta.type != "document management system":
            raise ValueError()
        return type_doc

    @validator('company')
    def get_id_from_company(cls, company):
        if company.meta.type != "company":
            raise ValueError()
        return company


class Meta(TypedDict):
    href: str
    type: str

class DocumentCodeDoc(TypedDict):
    meta: Meta
    id: int
    code: str
    creator: Meta


class HandlerRequestAddCodeDoc(HandlerRequestGetData):
    """Обработчик запроса на получение всех бизнес процессов"""

    _data_from_request: dict

    def __init__(self, data_from_request):
        super().__init__()
        self._data_from_request = data_from_request

    def _create_document(self) -> DocumentCodeDoc:
        """Создает документ."""
        model = self._get_model_post_request()
        id = self._add_code_doc_to_db(model)
        code = self._get_code_doc(id)
        return DocumentCodeDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/code/{id}"),
                type="document management system"
            ),
            id=id,
            code=code,
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{self._authentication_user.user_id}"
                ),
                type="app users"
            ),
        )

    def _get_model_post_request(self) -> ModelCodeDoc:
        """Получает модель POST запроса."""
        try:
            model = ModelCodeDoc(**self._data_from_request)
        except ValidationError as e:
            self._set_error_in_handler_result(
                source=(
            f"Не удалось прочитать: {[fields['loc'] for fields in e.errors()]}"
                ),
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return model

    def _add_code_doc_to_db(self, model: ModelCodeDoc) -> int:
        """Добавляет код документ в базу данных. Возвращает id."""
        try:
            id_bpm = post_req_parser.get_id(
                path='/bpm',
                href=model.bpm.meta.href
            )
            id_type_doc = post_req_parser.get_id(
                path='/docs/types',
                href=model.type_doc.meta.href
            )
            id_company = post_req_parser.get_id(
                path='/company',
                href=model.company.meta.href
            )
        except post_req_parser.ErrorGettingID as e:
            self._set_error_in_handler_result(
                source= e.source,
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        data = db_docs.DataForAdd(
            id_bpm=id_bpm,
            id_type_doc=id_type_doc,
            id_company=id_company,
            id_creator=self._authentication_user.user_id
        )
        try:
            id = db_docs.add_code_doc(data)
        except db_docs.ErrorAddingCodeDoc:
            self._set_error_in_handler_result(
                source= "Неккоректные ID в ссылках",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id

    def _get_code_doc(self, id: int) -> str:
        """Получает код документа."""
        code_doc = CodeDoc.query.filter(CodeDoc.id == id).first()
        return f"{code_doc.bpm.code}-{code_doc.type_doc.abv}{code_doc.number}"








class MetaAllCodeDocs(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllCodeDocs(TypedDict):
    meta: MetaAllCodeDocs
    rows: list[DocumentCodeDoc]
