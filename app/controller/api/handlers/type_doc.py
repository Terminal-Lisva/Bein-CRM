from typing import TypedDict
from .handler import HandlerRequestGetData, HandlerError
from database.models.database import db
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


class HandlerRequestGetAllTypesDocs(HandlerRequestGetData):
    """Обработчик запроса на получение всех типов документов"""

    def __init__(self):
        super().__init__()

    def _get_models(self) -> list[db.Model]:
        """Получает модели."""
        return TypeDoc.query.all()

    def _create_document(self) -> DocumentAllTypesDocs:
        """Создает документ."""
        models = self._get_models()
        meta = MetaAllTypesDocs(
            href=for_api.make_href(path="/docs/types"),
            type="document management system",
            size=len(models)
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
            ) for model in models]
        return DocumentAllTypesDocs(meta=meta, rows=rows)
