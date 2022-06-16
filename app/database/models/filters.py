from database.models.database import db
from controller.api.query_string_parser import QueryStringParser, LogicCondition
from sqlalchemy import and_, or_, sql


class GetterModelsUsingCustomFilter:
    """Получатель моделей используя кастомный фильтр"""

    _model: type[db.Model]
    _parser: QueryStringParser

    def __init__(self, model, parser):
        self._model = model
        self._parser = parser

    def get(self) -> list[db.Model]:
        """Получает модель/список моделей."""
        list_logic_conditions = self._parser.get_list_logic_conditions()
        elements = [
            or_(*[self._create_element_for_filter_model(logic_condition)
                for logic_condition in logic_conditions])
                    for logic_conditions in list_logic_conditions
        ]
        return self._model.query.filter(and_(*elements)).all()

    def _create_element_for_filter_model(
        self,
        logic_condition: LogicCondition) -> sql.elements.BinaryExpression:
        """Создает элемент для фильтра модели."""
        match logic_condition.operator:
            case '=':
                condition = getattr(
                    self._model, logic_condition.key) == logic_condition.value
            case '!=':
                condition = getattr(
                    self._model, logic_condition.key) != logic_condition.value
            case 'in':
                condition = getattr(
                    self._model,logic_condition.key).in_(logic_condition.value)
            case '>':
                condition = getattr(
                    self._model, logic_condition.key) > logic_condition.value
            case '>=':
                condition = getattr(
                    self._model, logic_condition.key) >= logic_condition.value
            case '<':
                condition = getattr(
                    self._model, logic_condition.key) < logic_condition.value
            case '<=':
                condition = getattr(
                    self._model, logic_condition.key) <= logic_condition.value
            case _:
                assert False, 'Оператор логического условия не найден!'
        return condition
