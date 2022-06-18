from pydantic import BaseModel, validator
from datetime import date
from controller.api import post_req_parser
from typing import TypedDict
from .handler import (HandlerRequestAddData, HandlerError,
HandlerRequestGetAllResourcesUsingFilter, HandlerRequestChangeData)
from database.models.code_doc import CodeDoc
from controller.api.errors import Errors
from database import db_docs
from controller.api import for_api
from controller.api.query_string_parser import FieldQuery
from database.models.doc import Doc


def _forms_fullname_doc(id_code_doc: int, name_doc: str) -> str:
    """Формирует полное имя документа."""
    code_doc = CodeDoc.query.filter_by(id=id_code_doc).first()
    return (f'{code_doc.bpm.code}-{code_doc.type_doc.abv}{code_doc.number} '
            f'{code_doc.type_doc.name}: {name_doc}')


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
    def check_meta_code_doc(cls, code_doc):
        if code_doc.meta.type != "document management system":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/docs/code', href=code_doc.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id

    @validator('responsible')
    def check_meta_responsible(cls, responsible):
        if responsible.meta.type != "app users":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/users', href=responsible.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id


class Meta(TypedDict):
    href: str
    type: str

class DocumentDoc(TypedDict):
    meta: Meta
    id: int
    code_doc: Meta
    fullname: str
    date_start: date
    date_finish: date
    responsible: Meta
    version: int
    actual: bool
    creator: Meta


class HandlerRequestAddDoc(HandlerRequestAddData):
    """Обработчик запроса на добавление документа"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request, model=ModelDoc)

    def _check_code_doc(self, id_code_doc: int) -> None:
        """Проверяет код документа."""
        code_doc = CodeDoc.query.filter_by(id=id_code_doc).first()
        if code_doc is None:
            self._set_error_in_handler_result(
                source=f"/docs/code/{id_code_doc}",
                error=Errors.NOT_FOUND_PATH
            )
            raise HandlerError
        elif code_doc.used == 1:
            self._set_error_in_handler_result(
                source=f"Документ с таким кодом уже зарегистрирован",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        elif code_doc.id_creator != self._authentication_user.user_id:
            self._set_error_in_handler_result(
                source=f"Вы не являетесь владельцем кода документа",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return

    def _add_record_to_db(self, model_data: ModelDoc) -> int:
        """Добавляет запись в базу данных. Возвращает id записи."""
        self._check_code_doc(id_code_doc=model_data.code_doc)
        data = db_docs.DataForAddDoc(
            id_code_doc=model_data.code_doc,
            name=model_data.name,
            date_start=model_data.date_start,
            date_finish=model_data.date_finish,
            id_responsible=model_data.responsible,
            id_creator=self._authentication_user.user_id
        )
        try:
            id_record = db_docs.add_doc(data)
        except Exception:
            self._set_error_in_handler_result(
                source="ID не найдены",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        return id_record

    def _create_document(self, model_data: ModelDoc, id_doc: int)-> DocumentDoc:
        """Создает документ."""
        return DocumentDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/{id_doc}"),
                type="document management system"
            ),
            id=id_doc,
            code_doc=Meta(
                href=for_api.make_href(path=f"/docs/code/{model_data.code_doc}"),
                type="document management system"
            ),
            fullname=_forms_fullname_doc(
                id_code_doc=model_data.code_doc,
                name_doc=model_data.name
            ),
            date_start=model_data.date_start,
            date_finish=model_data.date_finish,
            responsible=Meta(
                href=for_api.make_href(
                    path=f"/users/{model_data.responsible}"
                ),
                type="app users"
            ),
            version=1,
            actual=True,
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{self._authentication_user.user_id}"
                ),
                type="app users"
            )
        )


class MetaAllDocs(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllDocs(TypedDict):
    meta: MetaAllDocs
    rows: list[DocumentDoc]


class HandlerRequestGetAllDocs(HandlerRequestGetAllResourcesUsingFilter):
    """Обработчик запроса на получение всех документов"""

    def __init__(self, query_string):
        super().__init__(query_string, cls_orm_model=Doc)

    def _get_fields_query(self) -> list[FieldQuery]:
        """Получает запрашиваемые поля."""
        return [
            FieldQuery(
                name_in_db='id_responsible',
                name='responsible',
                operators=['!=', '='],
                prefix=for_api.make_href(f"/users/"),
                null=False,
                type=str
            ),
            FieldQuery(
                name_in_db='actual',
                name='actual',
                operators=['!=', '='],
                prefix="",
                null=False,
                type=bool
            ),
            FieldQuery(
                name_in_db='id_creator',
                name='creator',
                operators=['!=', '='],
                prefix=for_api.make_href(f"/users/"),
                null=False,
                type=str
            ),
        ]

    def _create_document(self, orm_models: list[Doc]) -> DocumentAllDocs:
        """Создает документ."""
        meta = MetaAllDocs(
            href=for_api.make_href(path="/docs"),
            type="document management system",
            size=len(orm_models)
        )
        rows = [DocumentDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/{model.id}"),
                type="document management system"
            ),
            id=model.id,
            code_doc=Meta(
                href=for_api.make_href(path=f"/docs/code/{model.id_code_doc}"),
                type="document management system"
            ),
            fullname=_forms_fullname_doc(
                id_code_doc=model.id_code_doc,
                name_doc=model.name
            ),
            date_start=model.date_start,
            date_finish=model.date_finish,
            responsible=Meta(
                href=for_api.make_href(
                    path=f"/users/{model.id_responsible}"
                ),
                type="app users"
            ),
            version=model.version,
            actual=bool(model.actual),
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{model.id_creator}"
                ),
                type="app users"
                )
            ) for model in orm_models]
        return DocumentAllDocs(meta=meta, rows=rows)


class ModelUpdatedDoc(BaseModel):
    date_start: date
    date_finish: date
    responsible: ModelField

    @validator('responsible')
    def check_meta_responsible(cls, responsible):
        if responsible.meta.type != "app users":
            raise ValueError()
        try:
            id = post_req_parser.get_id(path='/users', href=responsible.meta.href)
        except post_req_parser.ErrorGettingID:
            raise ValueError()
        return id


class HandlerRequestUpdatingVersionDoc(HandlerRequestChangeData):
    """Обработчик запроса на обновление версии документа"""

    def __init__(self, id_doc, data_from_request):
        super().__init__(
            data_from_request,
            model=ModelUpdatedDoc,
            id=id_doc,
            cls_orm_model=Doc
        )

    def _check_possibility_updating_version_doc(self) -> None:
        """Проверяет возможность обновления версии документа."""
        doc = self._get_orm_model()
        if doc is None:
            self._set_error_in_handler_result(
                source=f"/docs/{self._id}",
                error=Errors.NOT_FOUND_PATH
            )
            raise HandlerError
        elif doc.id_creator != self._authentication_user.user_id:
            self._set_error_in_handler_result(
                source="Вы не являетесь создателем документа",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError
        elif doc.actual == 0:
            self._set_error_in_handler_result(
                source="Документ неактуален",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError

    def _change_record_to_db(self, model_data: BaseModel) -> None:
        """Изменяет запись в базе данных."""
        self._check_possibility_updating_version_doc()
        data = db_docs.DataForUpdateDoc(
            id_doc=self._id,
            date_start=model_data.date_start,
            date_finish=model_data.date_finish,
            id_responsible=model_data.responsible,
        )
        try:
            db_docs.updates_version_doc(data)
        except Exception:
            self._set_error_in_handler_result(
                source="ID ответственного не найден",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError

    def _create_document(self, orm_model: Doc) -> DocumentDoc:
        """Создает документ."""
        return DocumentDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/{orm_model.id}"),
                type="document management system"
            ),
            id=self._id,
            code_doc=Meta(
                href=for_api.make_href(
                    path=f"/docs/code/{orm_model.id_code_doc}"
                ),
                type="document management system"
            ),
            fullname=_forms_fullname_doc(
                id_code_doc=orm_model.id_code_doc,
                name_doc=orm_model.name
            ),
            date_start=orm_model.date_start,
            date_finish=orm_model.date_finish,
            responsible=Meta(
                href=for_api.make_href(
                    path=f"/users/{orm_model.id_responsible}"
                ),
                type="app users"
            ),
            version=orm_model.version,
            actual=bool(orm_model.actual),
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{orm_model.id_creator}"
                ),
                type="app users"
            )
        )


class ModelChangeActualDoc(BaseModel):
    actual: bool


class HandlerRequestChangeActualDoc(HandlerRequestChangeData):
    """Обработчик запроса на изменение актуальности документа"""

    def __init__(self, id_doc, data_from_request):
        super().__init__(
            data_from_request,
            model=ModelChangeActualDoc,
            id=id_doc,
            cls_orm_model=Doc
        )

    def _check_possibility_change_actual_doc(self) -> None:
        """Проверяет возможность изменения актуальности документа."""
        doc = self._get_orm_model()
        if doc is None:
            self._set_error_in_handler_result(
                source=f"/docs/{self._id}",
                error=Errors.NOT_FOUND_PATH
            )
            raise HandlerError
        elif doc.id_creator != self._authentication_user.user_id:
            self._set_error_in_handler_result(
                source="Вы не являетесь создателем документа",
                error=Errors.BAD_REQUEST
            )
            raise HandlerError

    def _change_record_to_db(self, model_data: BaseModel) -> None:
        """Изменяет запись в базе данных."""
        self._check_possibility_change_actual_doc()
        data = db_docs.DataForChangeDoc(
            id_doc=self._id,
            actual=int(model_data.actual),
        )
        db_docs.change_actual_doc(data)

    def _create_document(self, orm_model: Doc) -> DocumentDoc:
        """Создает документ."""
        return DocumentDoc(
            meta=Meta(
                href=for_api.make_href(path=f"/docs/{orm_model.id}"),
                type="document management system"
            ),
            id=self._id,
            code_doc=Meta(
                href=for_api.make_href(
                    path=f"/docs/code/{orm_model.id_code_doc}"
                ),
                type="document management system"
            ),
            fullname=_forms_fullname_doc(
                id_code_doc=orm_model.id_code_doc,
                name_doc=orm_model.name
            ),
            date_start=orm_model.date_start,
            date_finish=orm_model.date_finish,
            responsible=Meta(
                href=for_api.make_href(
                    path=f"/users/{orm_model.id_responsible}"
                ),
                type="app users"
            ),
            version=orm_model.version,
            actual=orm_model.actual,
            creator=Meta(
                href=for_api.make_href(
                    path=f"/users/{orm_model.id_creator}"
                ),
                type="app users"
            )
        )
