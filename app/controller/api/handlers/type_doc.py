from typing import TypedDict
from .handler import HandlerRequestGetAllResources
from database.models.type_doc import TypeDoc
from controller.api import for_api


class Meta(TypedDict):
    href: str
    type: str

class DocumentTypeDoc(TypedDict):
    meta: Meta
    id: int
    name: str
    layer: str

class MetaAllTypesDocs(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllTypesDocs(TypedDict):
    meta: MetaAllTypesDocs
    rows: list[DocumentTypeDoc]


class HandlerRequestGetAllTypesDocs(HandlerRequestGetAllResources):
    """Обработчик запроса на получение всех типов документов"""

    def __init__(self):
        super().__init__(cls_orm_model=TypeDoc)

    def _create_document(self, orm_models:list[TypeDoc])-> DocumentAllTypesDocs:
        """Создает документ."""
        meta = MetaAllTypesDocs(
            href=for_api.make_href(path="/docs/types"),
            type="document management system",
            size=len(orm_models)
        )
        rows = [
            DocumentTypeDoc(
                meta=Meta(
                    href=for_api.make_href(path=f"/docs/types/{model.id}"),
                    type="document management system"
                ),
                id=model.id,
                name=model.name,
                layer=model.layer
            ) for model in orm_models]
        return DocumentAllTypesDocs(meta=meta, rows=rows)
