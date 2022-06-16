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
        super().__init__()

    def _create_document(self) -> DocumentAllCompany:
        """Создает документ."""
        models = self._get_orm_models(cls_model=Company)
        meta = MetaAllCompany(
            href=for_api.make_href(path="/company"),
            type="company",
            size=len(models)
        )
        rows = [
            DocumentCompany(
                meta=Meta(
                    href=for_api.make_href(path=f"/company/{model.id}"),
                    type="company"
                ),
                id=model.id,
                name=model.name
            ) for model in models]
        return DocumentAllCompany(meta=meta, rows=rows)


class HandlerRequestGetCompany(HandlerRequestGetResource):
    """Обработчик запроса на получение компании"""

    def __init__(self, company_id):
        super().__init__(company_id)

    def _create_document(self) -> DocumentCompany:
        """Создает документ."""
        model = self._get_orm_model(cls_model=Company)
        return DocumentCompany(
            meta=Meta(
                href=for_api.make_href(path=f"/company/{model.id}"),
                type="company"
            ),
            id=model.id,
            name=model.name
        )
