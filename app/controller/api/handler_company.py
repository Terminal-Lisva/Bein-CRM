from typing import TypedDict, Literal
from .handler import (HandlerRequestWithAuthentication, HandlerResult,
make_href_meta, ExcHandlerError)
from database.models.company import Company
from enum import Enum


class DocumentCompany(TypedDict):
    meta: dict[Literal["href", "type"], str]
    id: int
    name: str


class MetaAllCompany(TypedDict):
    href: str
    type: str
    size: int


class DocumentAllCompany(TypedDict):
    meta: MetaAllCompany
    rows: list[DocumentCompany]


class HandlerRequestGetAllCompany(HandlerRequestWithAuthentication):
    """Обработчик запроса на получение всех компаний"""

    def __init__(self):
        super().__init__()

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на получение компаний."""
        if not self._check_authentication_user():
            return HandlerResult()
        document = self.__create_document()
        return HandlerResult(document, status_code=200)

    def __create_document(self) -> DocumentAllCompany:
        """Создает документ."""
        company = Company.query.all()
        meta = MetaAllCompany(
            href=make_href_meta(path="/company"),
            type="company",
            size=len(company)
        )
        rows = [DocumentCompany(
            meta={
                "href": make_href_meta(path=f"/company/{row.id}"),
                "type": "company"
            },
            id=row.id,
            name=row.name
        ) for row in company]
        return DocumentAllCompany(meta=meta, rows=rows)


class Errors(Enum):
    """Ошибки"""
    ID_NOT_FOUND = 1


class HandlerRequestGetCompany(HandlerRequestWithAuthentication):
    """Обработчик запроса на получение компании"""

    __company_id: int

    def __init__(self, company_id):
        super().__init__()
        self.__company_id = company_id

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на получение компаний."""
        if not self._check_authentication_user():
            return HandlerResult()
        document = self.__create_document()
        return HandlerResult(document, status_code=200)

    def __create_document(self) -> DocumentCompany:
        """Создает документ."""
        path = f"/company/{self.__company_id}"
        company = Company.query.get(self.__company_id)
        if company is None:
            self._set_handler_error(
                source=path,
                type="BAD_REQUEST",
                enum=Errors.ID_NOT_FOUND
            )
            raise ExcHandlerError
        return DocumentCompany(
            meta={
                "href": make_href_meta(path),
                "type": "company"
            },
            id=company.id,
            name=company.name
        )
