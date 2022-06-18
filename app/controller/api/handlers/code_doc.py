from pydantic import BaseModel, validator
from controller.api import post_req_parser
from typing import TypedDict
from .handler import (HandlerRequestAddData, HandlerRequestDelData,
HandlerError, HandlerRequestGetAllResourcesUsingFilter)
from controller.api.errors import Errors
from database import db_docs
from database.models.code_doc import CodeDoc
from controller.api import for_api
from controller.api.query_string_parser import FieldQuery


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
    def check_meta_bpm(cls, bpm):
        if bpm.meta.type != "process management":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/bpm', href=bpm.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id

    @validator('type_doc')
    def check_meta_type_doc(cls, type_doc):
        if type_doc.meta.type != "document management system":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/docs/types', href=type_doc.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id

    @validator('company')
    def check_meta_company(cls, company):
        if company.meta.type != "company":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/company', href=company.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id


class Meta(TypedDict):
    href: str
    type: str

class DocumentCodeDoc(TypedDict):
    meta: Meta
    id: int
    code: str
    creator: Meta
    company: Meta
    used: bool


class HandlerRequestAddCodeDoc(HandlerRequestAddData):
    """Обработчик запроса на добавление кода документа"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request, model=ModelCodeDoc)

    def _forms_code_doc(self, id_code_doc: int) -> str:
        """Формирует код документа."""
        code_doc = CodeDoc.query.filter_by(id=id_code_doc).first()
        return f"{code_doc.bpm.code}-{code_doc.type_doc.abv}{code_doc.number}"

    def _add_record_to_db(self, model_data: ModelCodeDoc) -> int:
        """Добавляет запись в базу данных. Возвращает id записи."""
        data = db_docs.DataForAddCodeDoc(
            id_bpm=model_data.bpm,
            id_type_doc=model_data.type_doc,
            id_company=model_data.company,
            id_creator=self._authentication_user.user_id
        )
        try:
            id_record = db_docs.add_code_doc(data)
        except Exception:
            self._set_error_in_handler_result(
                source="ID не найдены",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id_record

    def _create_document(
        self,
        model_data: ModelCodeDoc,
        id_code_doc: int
        ) -> DocumentCodeDoc:
        """Создает документ."""
        return DocumentCodeDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/code/{id_code_doc}"),
                type="document management system"
            ),
            id=id_code_doc,
            code=self._forms_code_doc(id_code_doc),
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{self._authentication_user.user_id}"
                ),
                type="app users"
            ),
            company=Meta(
                href=for_api.make_href(path=f"/company/{model_data.company}"),
                type="company"
            ),
            used=False
        )


class HandlerRequestDelCodeDoc(HandlerRequestDelData):
    """Обработчик запроса на удаление кода документа"""

    def __init__(self, id_code_doc):
        super().__init__(id_code_doc, cls_orm_model=CodeDoc)

    def _make_appeal_db(self) -> None:
        """Делает обращение к БД."""
        self._check_code_doc()
        db_docs.del_code_doc(self._id)

    def _check_code_doc(self) -> None:
        """Проверяет код документа."""
        code_doc = self._get_orm_model()
        if code_doc.id_creator != self._authentication_user.user_id:
            self._set_error_in_handler_result(
                source="Вы не являетесь создателем кода документа",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        elif code_doc.used != 0:
            self._set_error_in_handler_result(
                source="Документ с таким кодом уже зарегистрирован",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError


class MetaAllCodeDocs(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllCodeDocs(TypedDict):
    meta: MetaAllCodeDocs
    rows: list[DocumentCodeDoc]


class HandlerRequestGetAllCodeDocs(HandlerRequestGetAllResourcesUsingFilter):
    """Обработчик запроса на получение всех кодов документов"""

    def __init__(self, query_string):
        super().__init__(query_string, cls_orm_model=CodeDoc)

    def _get_fields_query(self) -> list[FieldQuery]:
        """Получает запрашиваемые поля."""
        return [
            FieldQuery(
                name_in_db='id_creator',
                name='creator',
                operators=['!=', '='],
                prefix=for_api.make_href(f"/users/"),
                null=False,
                type=str
            ),
            FieldQuery(
                name_in_db='used',
                name='used',
                operators=['!=', '='],
                prefix="",
                null=False,
                type=bool
            )
        ]

    def _create_document(self, orm_models:list[CodeDoc]) -> DocumentAllCodeDocs:
        """Создает документ."""
        meta = MetaAllCodeDocs(
            href=for_api.make_href(path="/docs/code"),
            type="document management system",
            size=len(orm_models)
        )
        rows = [
            DocumentCodeDoc(
                meta=Meta(
                    href=for_api.make_href(path=f"/docs/code/{model.id}"),
                    type="document management system"
                ),
                id=model.id,
                code=f"{model.bpm.code}-{model.type_doc.abv}{model.number}",
                creator=Meta(
                    href=for_api.make_href(path=f"/users/{model.id_creator}"),
                    type="app users"
                ),
                company=Meta(
                    href=for_api.make_href(path=f"/company/{model.id_company}"),
                    type="company"
                ),
                used=bool(model.used)
            ) for model in orm_models]
        return DocumentAllCodeDocs(meta=meta, rows=rows)
