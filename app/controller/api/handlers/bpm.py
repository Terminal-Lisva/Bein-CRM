from typing import TypedDict
from .handler import HandlerRequestGetAllResourcesUsingFilter
from controller.api import for_api
from database.models.bpm import Bpm
from controller.api.query_string_parser import FieldQuery


class Meta(TypedDict):
    href: str
    type: str

class DocumentBpm(TypedDict):
    meta: Meta
    id: int
    code: str
    name: str
    lvl: int
    company: Meta
    parent: Meta | None

class MetaAllBpm(TypedDict):
    href: str
    type: str
    size: int

class DocumentAllBpm(TypedDict):
    meta: MetaAllBpm
    rows: list[DocumentBpm]


class HandlerRequestGetAllBpm(HandlerRequestGetAllResourcesUsingFilter):
    """Обработчик запроса на получение всех бизнес процессов"""

    def __init__(self, query_string):
        super().__init__(query_string, cls_orm_model=Bpm)

    def _get_fields_query(self) -> list[FieldQuery]:
        """Получает поля запроса."""
        return [FieldQuery(
            name_in_db='id_parent',
            name='parent',
            operators=['!=', '='],
            prefix=for_api.make_href(f"/bpm/"),
            null=True,
            type=str
        )]

    def _create_document(self, orm_models: list[Bpm]) -> DocumentAllBpm:
        """Создает документ."""
        meta = MetaAllBpm(
            href=for_api.make_href(path="/bpm"),
            type="process management",
            size=len(orm_models)
        )
        rows = [
            DocumentBpm(
                meta=Meta(
                    href=for_api.make_href(path=f"/bpm/{model.id}"),
                    type="process management"
                ),
                id=model.id,
                code=model.code,
                name=model.name,
                lvl=model.lvl,
                company=Meta(
                    href=for_api.make_href(path=f"/company/{model.id_company}"),
                    type="company"
                ),
                parent=Meta(
                    href=for_api.make_href(path=f"/bpm/{model.id_parent}"),
                    type="process management"
                ) if model.lvl > 1 else None,
            ) for model in orm_models]
        return DocumentAllBpm(meta=meta, rows=rows)
