from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union, Optional, Tuple
from flask import typing as flaskTyping
from .page_funcs import (template_response, get_current_page_uri,
add_cookies_to_response)
from service_layer.user import User
from database import page_db


#Логика получения HTML страницы:
class ConstructorPageTemplate(ABC):
    """Базовый класс - Конструктор шаблона страницы"""

    _template: str

    def __init__(self, template):
        self._template = template

    @abstractmethod
    def creates(self, kwargs) -> flaskTyping.ResponseReturnValue:
        """Создает страницу."""
        raise NotImplementedError()


class ConstructorPageTemplateWithSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы с боковым меню"""

    def __init__(self, template):
        super().__init__(template)

    def creates(
        self,
        kwargs: Dict[str, Union[int, Tuple[str], Dict[Any, Any]]]
        ) -> flaskTyping.ResponseReturnValue:
        """Создает страницу с боковым меню.
        У пользователей разная видимость бокового меню."""
        side_menu_data = self.__get_tree_side_menu_data(kwargs.get('user_id'))
        page = template_response(
            self._template,
            data = {
                'side_menu_data': side_menu_data,
                'user_data': kwargs.get('user_data'),
                'supplement': kwargs.get('supplement', None)
            }
        )
        return page

    def __get_tree_side_menu_data(
        self,
        user_id #: int
        ) -> List[Dict[str, Union[str, list]]]:
        """Получает дерево данных бокового меню."""
        side_menu_data = page_db.get_side_menu_data(user_id)
        tree_side_menu_data: list = []
        def creates_tree(l, parent_id):
            for row in side_menu_data:
                item_id = row[0]
                item_name = row[1]
                parent_item_id = row[2]
                item_href = row[3]
                if parent_item_id == parent_id:
                    l.append({
                        'name': item_name,
                        'href': item_href,
                        'children': []
                    })
                    creates_tree(l[-1]['children'], item_id)
        creates_tree(l=tree_side_menu_data, parent_id=0)
        return tree_side_menu_data


class ConstructorPageTemplateWithoutSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы без бокового меню"""
    pass


class Page(ABC):
    """Базовый класс - Страница"""

    _constructor: ConstructorPageTemplate
    _user: User

    def __init__(self, constructor):
        self._constructor = constructor
        self._user = User()

    @abstractmethod
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        raise NotImplementedError()

    def _forms_response_page(self, **kwargs) -> flaskTyping.ResponseReturnValue:
        """Формирует ответ страницу."""
        response_page = self._constructor.creates(
            {
            'user_id': self._user.id,
            'user_data': self._user.get_data(),
            } | {'supplement': kwargs}
        )
        add_cookies_to_response(
            response_page,
            cookie_session = self._user.cookie_session
        )
        return response_page


class PageAvailable(Page):
    """Страница доступная (разрешение на ее просмотр не требуется)."""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        if not self._user:
            return "404"
        response_page = self._forms_response_page()
        return response_page


class PageWithPermitView(Page):
    """Страница с разрешением на ее просмотр"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ."""
        if not self._user or not self.__permit_view_page():
            return "404"
        response_page = self._forms_response_page()
        return response_page

    def __permit_view_page(self) -> bool:
        """Разрешение просмотра страницы."""
        page_uri = get_current_page_uri()
        permit = page_db.get_permit_view_page(self._user.id, page_uri)
        return permit
