from typing import Literal, NamedTuple, Iterable
from dataclasses import dataclass
import re
from itertools import groupby
import operator
import logging


OPERATORS = ['!=', '=', '>=', '>', '<=', '<']
Operators = list[Literal['!=', '=', '>=', '>', '<=', '<']]

class FieldQuery(NamedTuple):
    """Запрашиваемое поле"""
    name_in_db: str                 #'id_parent'
    name: str                       #'parent'
    operators: Operators            #['=', '!=']
    prefix: str                     #'http://web/bpm/'
    null: bool                      #True
    type: type                      #int


class ErrorQueryStringParsing(Exception):
    """Ошибка парсинга строки запроса"""

    def __init__(self, source):
        self.source = f'Не удалось прочитать: {source}'


@dataclass
class LogicCondition:
    """Логическое условие"""
    key: str
    operator: str
    value: int | str | bool | None | list

LogicConditions = list[LogicCondition]


class QueryStringParser:
    """Парсер строки запроса"""

    _string: str
    _fields: list[FieldQuery]

    def __init__(self, string, fields):
        self._string = string
        self._fields = fields

    def get_list_logic_conditions(self) -> list[LogicConditions]:
        """Получает список логических условий."""
        self._removes_spaces_in_string()
        conditions = self._finds_conditions()
        logging.getLogger('app_logger').debug(f"conditions: {conditions}")
        separate_conditions = self._separates_conditions(conditions)
        return list(self._forms_logic_conditions(separate_conditions))

    def _removes_spaces_in_string(self) -> None:
        """Удаляет пробелы в строке."""
        self._string.replace(" ", "")

    def _finds_conditions(self) -> list[str]:
        """Ищет условия внутри скобок."""
        class Interval(NamedTuple):
            start: int
            end: int

        pattern = re.compile(r"(\(.+?\))")
        text = self._string
        matchs = re.finditer(pattern, text)
        intervals = [Interval(match.start(), match.end()) for match in matchs]

        #Ничего не найдено
        if len(intervals) == 0: raise ErrorQueryStringParsing(source=text)

        #Может быть так: text = ""...(id=2)", interval = от 3 до 9
        elif len(intervals) == 1:
            interval = intervals[0]
            length_interval = interval.end - interval.start
            if length_interval != len(text):
                start = interval.start - 1 if interval.start > 0 else 0
                end = interval.end
                source = text[0:start] + " " + text[end:len(text)]
                raise ErrorQueryStringParsing(source)
            return [text[1:-1]]

        #Может быть так: text = ""...(id=2);(id=3)", intervals = (3,9), (10,16)
        length_intervals = intervals[-1].end - intervals[0].start
        if length_intervals != len(text):
            start = intervals[0].start - 1 if intervals[0].start > 0 else 0
            end = intervals[-1].end
            source = text[0:start] + " " + text[end:len(text)]
            raise ErrorQueryStringParsing(source)

        #Может быть так: text = "(id=2)...(id=3)" или "(id=2);(id=3)"
        for i in range(1, len(intervals)):
            prev_interval = intervals[i-1]
            interval = intervals[i]
            if (prev_interval.end + 1 != interval.start
                or text[prev_interval.end] != ","):
                source = text[prev_interval.end:interval.start]
                raise ErrorQueryStringParsing(source)
        return [text[interval.start+1:interval.end-1] for interval in intervals]

    def _separates_conditions(
        self,
        conditions: list[str]) -> list[list[str]]:
        """Отделяет условия по ";"."""
        return [condition.split(';') for condition in conditions]

    def _forms_logic_conditions(
        self,
        separate_conditions: list[list[str]]) -> Iterable[LogicConditions]:
        """Формирует список логических условий."""
        for condition in separate_conditions:
            logic_conditions = []
            for i, element in enumerate(condition):
                pars_element = self._parses_element(element)
                logic_condition = self._creates_logic_condition(pars_element)
                logic_conditions.append(logic_condition)
            yield self._groups_logic_сonditions(logic_conditions)

    def _parses_element(self, element: str) -> dict[str, str]:
        """Парсит разделенный элемент. Райзим исключение если ничего не нашли"""
        for operator in OPERATORS:
            pattern = f'(?P<key>\w+)(?P<operator>{operator})(?P<value>.+)'
            match = re.match(pattern, element)
            logging.getLogger('app_logger').debug(f"pars_element: {match}")
            if match is not None:
                return match.groupdict()
        raise ErrorQueryStringParsing(element)

    def _creates_logic_condition(
        self,
        pars_element: dict[str, str]) -> LogicCondition:
        """Создает логическое условие."""
        def del_prefix(text, prefix):
            pattern = f'(?P<prefix>{prefix})(?P<value>\w+)'
            match = re.match(pattern, text)
            if match is None: raise ErrorQueryStringParsing(text)
            return text[len(prefix):]

        key = pars_element["key"]
        operator = pars_element["operator"]
        value = pars_element["value"]

        field = None
        for _field in self._fields:
            if _field.name == key:
                field = _field; break
        if field is None: raise ErrorQueryStringParsing(key)

        if field.null and value == "null":
            return LogicCondition(
                key=field.name_in_db,
                operator=operator,
                value=None
            )
        elif field.type == bool and value in ['true', 'false']:
            return LogicCondition(
                key=field.name_in_db,
                operator=operator,
                value=value
            )
        value_without_prefix = del_prefix(value, field.prefix)
        if field.type == int and value_without_prefix.isdecimal():
            return LogicCondition(
                key=field.name_in_db,
                operator=operator,
                value=int(value_without_prefix)
            )
        elif field.type == str:
            return LogicCondition(
                key=field.name_in_db,
                operator=operator,
                value=value_without_prefix
            )
        else:
            raise ErrorQueryStringParsing(value)

    def _groups_logic_сonditions(
        self,
        logic_conditions: LogicConditions) -> list[LogicCondition]:
        """Группирует логические условия."""
        sorted_logic_conditions = sorted(
            logic_conditions,
            key=lambda logic_condition: logic_condition.key,
            reverse=True
        )
        grouped_logic_conditions = []
        for k, g in groupby(sorted_logic_conditions,operator.attrgetter('key')):
            grouping_list = list(g)
            if len(grouping_list) > 1:
                grouped_logic_conditions.append(
                    LogicCondition(
                        key=grouping_list[0].key,
                        operator='in',
                        value=[obj.value for obj in grouping_list]
                    )
                )
            else:
                grouped_logic_conditions.append(grouping_list[0])
        logging.getLogger('app_logger').debug(
            f"grouped_logic_conditions: {grouped_logic_conditions}")
        return grouped_logic_conditions
