from typing import TypedDict
from .handler import HandlerRequestGetData, HandlerError
from database.models.database import db
from database.models.company import Company
from controller.api import for_api
from controller.api.errors import Errors


class Meta(TypedDict):
    href: str
    type: str

class DocumentCompany(TypedDict):
    meta: Meta
    id: int
    name: str

class MetaAllCompany(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllCompany(TypedDict):
    meta: MetaAllCompany
    rows: list[DocumentCompany]


class HandlerRequestGetAllCompany(HandlerRequestGetData):
    """Обработчик запроса на получение всех компаний"""

    def __init__(self):
        super().__init__()

    def _get_model(self) -> db.Model:
        """Получает модель."""
        return Company.query.all()

    def _create_document(self, model: db.Model) -> DocumentAllCompany:
        """Создает документ."""
        meta = MetaAllCompany(
            href=for_api.make_href(path="/company"),
            type="company",
            size=len(model)
        )
        rows = [
            DocumentCompany(
                meta=Meta(
                    href=for_api.make_href(path=f"/company/{row.id}"),
                    type="company"
                ),
                id=row.id,
                name=row.name
            ) for row in model]
        return DocumentAllCompany(meta=meta, rows=rows)


class HandlerRequestGetCompany(HandlerRequestGetData):
    """Обработчик запроса на получение компании"""

    __company_id: int

    def __init__(self, company_id):
        super().__init__()
        self.__company_id = company_id

    def _get_model(self) -> db.Model:
        """Получает модель."""
        model = Company.query.get(self.__company_id)
        if model is None:
            self._set_error_in_handler_result(
                source=f"/company/{self.__company_id}",
                error=Errors.NOT_FOUND_PATH
            )
            raise HandlerError
        return model

    def _create_document(self, model: db.Model) -> DocumentCompany:
        """Создает документ."""
        return DocumentCompany(
            meta=Meta(
                href=for_api.make_href(path=f"/company/{model.id}"),
                type="company"
            ),
            id=model.id,
            name=model.name
        )
