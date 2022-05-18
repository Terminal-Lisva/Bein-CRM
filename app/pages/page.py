from typing import Any, List, Dict, Union, Optional
from abc import ABC, abstractmethod
from flask import typing as flaskTyping
from .page_funcs import template_response, get_current_page_uri, get_cookie, add_cookie_session_to_response
from service_layer.user_authentication import UserAuthenticationInfo, AuthenticationByCookies
from database import page_db


class ConstructorPageTemplate(ABC):
    """Конструктор шаблона страницы"""

    _template: str

    def __init__(self, template):
        self._template = template

    @abstractmethod
    def creates() -> flaskTyping.ResponseReturnValue:
        """Создает страницу."""
        raise NotImplementedError()


class ConstructorPageTemplateWithSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы с боковым меню"""

    def __init__(self, template):
        super().__init__(template)
    
    def creates(self, user_id: int, page_uri: str, *args: Any) -> flaskTyping.ResponseReturnValue:
        """Создает страницу с боковым меню. У пользователей разные права просмотра бокового меню."""
        side_menu_data = self.__get_tree_side_menu_data(user_id)
        page = template_response(
            self._template,
            data = {
                'side_menu': {
                    'side_menu_data': side_menu_data,
                    'page_uri': page_uri
                }, 
                'supplement': args
            }
        )
        return page


    def __get_tree_side_menu_data(self, user_id: int) -> List[Dict[str, Union[str, list]]]:
        """Получает дерево данных бокового меню."""
        side_menu_data = page_db.get_side_menu_data(user_id)
        tree_side_menu_data = []
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


class Page(ABC):
    """Базовый класс страница"""

    _page_uri: str
    _constructor: ConstructorPageTemplate
    __user_authentication_info: UserAuthenticationInfo

    def __init__(self, constructor):
        self._page_uri = get_current_page_uri()
        self._constructor = constructor
        self.__user_authentication_info = self.__authenticates_user() 
    
    def __authenticates_user(self) -> UserAuthenticationInfo:
        """Аутентифицирует пользователя."""
        cookie_session = get_cookie("Session")
        cookie_auth = get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth).get_user_authentication_info()
    
    @abstractmethod
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        raise NotImplementedError()
    
    def _get_user_id(self) -> Optional[int]:
        """Получает id пользователя."""
        return self.__user_authentication_info.user_id
    
    def _get_cookie_session(self) -> Optional[str]:
        """Получает куки сессии."""
        return self.__user_authentication_info.cookie_session

    def _permit_view_page(self, user_id: int) -> bool:
        """Разрешение просмотра страницы."""
        permit = page_db.get_permit_view_page(user_id, self._page_uri)
        return permit


class PageWithSideMenu(Page):
    """Страница с боковым меню"""

    def __init__(self, template: str):
        constructor = ConstructorPageTemplateWithSideMenu(template)
        super().__init__(constructor)
    
    def _forms_response_page(self, user_id: int) -> flaskTyping.ResponseReturnValue:
        """Формирует ответ страницу."""
        response_page = self._constructor.creates(user_id, self._page_uri)
        add_cookie_session_to_response(
            response_page, 
            cookie_session = self._get_cookie_session()
        )
        return response_page