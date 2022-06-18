from typing import TypedDict
from .handler import HandlerRequestGetAllResources, HandlerRequestGetResource
from database.models.company import Company
from controller.api import for_api


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


class HandlerRequestGetAllCompany(HandlerRequestGetAllResources):
    """Обработчик запроса на получение всех компаний"""

    def __init__(self):
        super().__init__(cls_orm_model=Company)

    def _create_document(self, orm_models: list[Company]) -> DocumentAllCompany:
        """Создает документ."""
        meta = MetaAllCompany(
            href=for_api.make_href(path="/company"),
            type="company",
            size=len(orm_models)
        )
        rows = [
            DocumentCompany(
                meta=Meta(
                    href=for_api.make_href(path=f"/company/{model.id}"),
                    type="company"
                ),
                id=model.id,
                name=model.name
            ) for model in orm_models]
        return DocumentAllCompany(meta=meta, rows=rows)


class HandlerRequestGetCompany(HandlerRequestGetResource):
    """Обработчик запроса на получение компании"""

    def __init__(self, company_id):
        super().__init__(company_id, cls_orm_model=Company)

    def _create_document(self, orm_model: Company) -> DocumentCompany:
        """Создает документ."""
        return DocumentCompany(
            meta=Meta(
                href=for_api.make_href(path=f"/company/{orm_model.id}"),
                type="company"
            ),
            id=orm_model.id,
            name=orm_model.name
        )
