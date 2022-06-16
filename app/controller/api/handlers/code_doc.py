from pydantic import BaseModel, validator
from controller.api import post_req_parser
from typing import TypedDict
from .handler import (HandlerRequestAddData, HandlerRequestWithAuthentication,
HandlerResult, HandlerError, HandlerRequestGetAllResourcesUsingFilter)
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
    status: int


class HandlerRequestAddCodeDoc(HandlerRequestAddData):
    """Обработчик запроса на добавление кода документа"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request)

    def _forms_code_doc(self, id_code_doc: int) -> str:
        """Формирует код документа."""
        code_doc = CodeDoc.query.filter_by(id=id_code_doc).first()
        return f"{code_doc.bpm.code}-{code_doc.type_doc.abv}{code_doc.number}"

    def _create_document(self) -> DocumentCodeDoc:
        """Создает документ."""
        model_data = self._get_model_data_post_request(ModelCodeDoc)
        id_code_doc = self._add_record_to_db(
            data=db_docs.DataForAddCodeDoc(
                id_bpm=model_data.bpm,
                id_type_doc=model_data.type_doc,
                id_company=model_data.company,
                id_creator=self._authentication_user.user_id
            ),
            db_func = db_docs.add_code_doc
        )
        code = self._forms_code_doc(id_code_doc)
        return DocumentCodeDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/code/{id_code_doc}"),
                type="document management system"
            ),
            id=id_code_doc,
            code=code,
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
            status=1
        )


class HandlerRequestDelCodeDoc(HandlerRequestWithAuthentication):
    """Обработчик запроса на удаление кода документа"""

    _id_code_doc: int

    def __init__(self, id_code_doc):
        super().__init__()
        self._id_code_doc = id_code_doc

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на получение данных."""
        if not self._check_authentication_user():
            return self._handler_result
        try:
            code_doc = self._get_model()
        except HandlerError:
            return self._handler_result
        if not self._check_creator_code_doc(code_doc):
            self._set_error_in_handler_result(
                source="Вы не являетесь создателем кода документа",
                error=Errors.BAD_REQUEST
            )
            return self._handler_result
        elif not self._check_status_code_doc(code_doc):
            self._set_error_in_handler_result(
                source="Документ с таким кодом уже зарегистрирован",
                error=Errors.BAD_REQUEST
            )
            return self._handler_result
        self._delete_code_doc()
        self._handler_result.document = {}
        self._handler_result.status_code = 204
        return self._handler_result

    def _get_model(self) -> CodeDoc:
        """Получает модель."""
        code_doc = CodeDoc.query.filter_by(id=self._id_code_doc).first()
        if code_doc is None:
            self._set_error_in_handler_result(
                source=f"/docs/code/{self._id_code_doc}",
                error=Errors.NOT_FOUND_PATH
            )
            raise HandlerError
        return code_doc

    def _check_creator_code_doc(self, code_doc: CodeDoc) -> bool:
        """Проверить создателя кода документа."""
        return code_doc.id_creator == self._authentication_user.user_id

    def _check_status_code_doc(self, code_doc: CodeDoc) -> bool:
        """Проверяет статус кода документа."""
        return code_doc.status == 1

    def _delete_code_doc(self) -> None:
        """Удаляет код документа."""
        db_docs.del_code_doc(self._id_code_doc)


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
        super().__init__(query_string)

    def _get_fields_query(self) -> list[FieldQuery]:
        """Получает поля запроса."""
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
                name_in_db='status',
                name='status',
                operators=['!=', '='],
                prefix="",
                null=False,
                type=int
            )
        ]

    def _create_document(self) -> DocumentAllCodeDocs:
        """Создает документ."""
        models = self._get_orm_models(CodeDoc)
        meta = MetaAllCodeDocs(
            href=for_api.make_href(path="/docs/code"),
            type="document management system",
            size=len(models)
        )
        rows = [
            DocumentCodeDoc(
                meta = Meta(
                    href=for_api.make_href(path=f"/docs/code/{model.id}"),
                    type="document management system"
                ),
                id = model.id,
                code = f"{model.bpm.code}-{model.type_doc.abv}{model.number}",
                creator = Meta(
                    href=for_api.make_href(path=f"/users/{model.id_creator}"),
                    type="app users"
                ),
                company=Meta(
                    href=for_api.make_href(path=f"/company/{model.id_company}"),
                    type="company"
                ),
                status=model.status
            ) for model in models]
        return DocumentAllCodeDocs(meta=meta, rows=rows)
