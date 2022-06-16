from pydantic import BaseModel, validator, ValidationError
from typing import TypedDict
from .handler import (HandlerRequestGetData, HandlerError,
HandlerRequestWithAuthentication, HandlerResult)
from controller.api.errors import Errors
from controller.api import post_req_parser
from database import db_docs
from database.models.code_doc import CodeDoc
from controller.api import for_api
from controller.api.query_string_parser import (QueryStringParser, FieldQuery,
ErrorQueryStringParsing)
from database.models.filters import GetterModelsUsingCustomFilter


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
    def check_type_meta_bpm(cls, bpm):
        if bpm.meta.type != "process management":
            raise ValueError()
        return bpm

    @validator('type_doc')
    def check_type_meta_type_doc(cls, type_doc):
        if type_doc.meta.type != "document management system":
            raise ValueError()
        return type_doc

    @validator('company')
    def check_type_meta_company(cls, company):
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
    company: Meta
    status: int


class HandlerRequestAddCodeDoc(HandlerRequestGetData):
    """Обработчик запроса на получение всех бизнес процессов"""

    _data_from_request: dict

    def __init__(self, data_from_request):
        super().__init__()
        self._data_from_request = data_from_request

    def _create_document(self) -> DocumentCodeDoc:
        """Создает документ."""
        model = self._get_model_post_request()
        ids = self._get_ids_from_model(model)
        id_code_doc = self._add_code_doc_to_db(ids)
        code = self._get_code_doc(id_code_doc)
        return DocumentCodeDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/code/{id}"),
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
                href=for_api.make_href(path=f"/company/{ids[2]}"),
                type="company"
            ),
            status=1
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

    def _get_ids_from_model(self, model: ModelCodeDoc) -> tuple[int, int, int]:
        """Получает id-ки из модели."""
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
        return id_bpm, id_type_doc, id_company

    def _add_code_doc_to_db(self, ids: tuple[int, int, int]) -> int:
        """Добавляет код документ в базу данных. Возвращает id кода док-та."""
        id_bpm, id_type_doc, id_company = ids
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
                source="Неккоректные ID",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id_code_doc

    def _get_code_doc(self, id_code_doc: int) -> str:
        """Получает код документа."""
        code_doc = CodeDoc.query.filter_by(id=id_code_doc).first()
        return f"{code_doc.bpm.code}-{code_doc.type_doc.abv}{code_doc.number}"


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
                source="Неккоректный ID",
                error=Errors.BAD_REQUEST
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


class HandlerRequestGetAllCodeDocs(HandlerRequestGetData):
    """Обработчик запроса на получение всех кодов документов"""

    _query_string: str | None

    def __init__(self, query_string):
        super().__init__()
        self._query_string = query_string

    def _get_models(self) -> list[CodeDoc]:
        """Получает модели."""
        if self._query_string is None:
            return CodeDoc.query.all()
        fields = [
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
        parser = QueryStringParser(string=self._query_string, fields=fields)
        try:
            models = GetterModelsUsingCustomFilter(
                model=CodeDoc,
                parser=parser).get()
        except ErrorQueryStringParsing as e:
            self._set_error_in_handler_result(
                source=e.source,
                error=Errors.FILTER_ERROR
            )
            raise HandlerError
        return models

    def _create_document(self) -> DocumentAllCodeDocs:
        """Создает документ."""
        models = self._get_models()
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
