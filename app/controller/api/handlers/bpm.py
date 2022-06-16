from typing import TypedDict
from .handler import HandlerRequestGetData, HandlerError
from controller.api import for_api
from controller.api.query_string_parser import (QueryStringParser, FieldQuery,
ErrorQueryStringParsing)
from database.models.filters import GetterModelsUsingCustomFilter
from database.models.bpm import Bpm
from controller.api.errors import Errors


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


class HandlerRequestGetAllBpm(HandlerRequestGetData):
    """Обработчик запроса на получение всех бизнес процессов"""

    _query_string: str | None

    def __init__(self, query_string):
        super().__init__()
        self._query_string = query_string

    def _get_models(self) -> list[Bpm]:
        """Получает модели."""
        if self._query_string is None:
            return Bpm.query.all()
        field = FieldQuery(
            name_in_db='id_parent',
            name='parent',
            operators=['!=', '='],
            prefix=for_api.make_href(f"/bpm/"),
            null=True,
            type=str
        )
        parser = QueryStringParser(string=self._query_string, fields=[field])
        try:
            models = GetterModelsUsingCustomFilter(
                model=Bpm,
                parser=parser).get()
        except ErrorQueryStringParsing as e:
            self._set_error_in_handler_result(
                source=e.source,
                error=Errors.FILTER_ERROR
            )
            raise HandlerError
        return models

    def _create_document(self) -> DocumentAllBpm:
        """Создает документ."""
        models = self._get_models()
        meta = MetaAllBpm(
            href=for_api.make_href(path="/bpm"),
            type="process management",
            size=len(models)
        )
        rows = [
            DocumentBpm(
                meta = Meta(
                    href=for_api.make_href(path=f"/bpm/{model.id}"),
                    type="process management"
                ),
                id = model.id,
                code = model.code,
                name = model.name,
                lvl = model.lvl,
                company = Meta(
                    href=for_api.make_href(path=f"/company/{model.id_company}"),
                    type="company"
                ),
                parent = Meta(
                    href=for_api.make_href(path=f"/bpm/{model.id_parent}"),
                    type="process management"
                ) if model.lvl > 1 else None,
            ) for model in models]
        return DocumentAllBpm(meta=meta, rows=rows)
