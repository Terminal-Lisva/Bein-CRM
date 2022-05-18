from typing import Any, List, Dict, Union, Optional, Tuple
from abc import ABC, abstractmethod
from flask import typing as flaskTyping
from .page_funcs import template_response, get_current_page_uri, get_cookie, add_cookie_session_to_response
from service_layer.user_authentication import UserAuthenticationInfo, AuthenticationByCookies
from database import page_db, user_db


class ConstructorPageTemplate(ABC):
    """Конструктор шаблона страницы"""

    _template: str

    def __init__(self, template):
        self._template = template

    @abstractmethod
    def creates() -> flaskTyping.ResponseReturnValue:
        """Создает страницу."""
        raise NotImplementedError()


# Разные варианты конструкторов страниц:
class ConstructorPageTemplateWithSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы с боковым меню"""

    def __init__(self, template):
        super().__init__(template)
    
    def creates(self, kwargs: Dict[str, Union[int, str, Any]]) -> flaskTyping.ResponseReturnValue:
        """Создает страницу с боковым меню. У пользователей разная видимость бокового меню."""
        user_id = kwargs.get('user_id')
        side_menu_data = self.__get_tree_side_menu_data(user_id)
        user_data = user_db.get_user_data(user_id)
        page = template_response(
            self._template,
            data = {
                'side_menu_data': side_menu_data,
                'user_data': user_data,
                'supplement': kwargs.get('page_uri', None)
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


class ConstructorPageTemplateWithoutSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы без бокового меню"""
    pass


class Page(ABC):
    """Базовый класс страница"""

    _constructor: ConstructorPageTemplate
    __user_authentication_info: UserAuthenticationInfo

    def __init__(self, constructor):
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
    
    def __get_cookie_session(self) -> Optional[str]:
        """Получает куки сессии."""
        return self.__user_authentication_info.cookie_session
    
    def _forms_response_page(self, **kwargs) -> flaskTyping.ResponseReturnValue:
        """Формирует ответ страницу."""
        response_page = self._constructor.creates(kwargs)
        add_cookie_session_to_response(
            response_page, 
            cookie_session = self.__get_cookie_session()
        )
        return response_page
    

#Разные варианты страниц:
class PageAvailable(Page):
    """Страница доступная (разрешение на ее просмотр не требуется)."""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)
    
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        user_id = self._get_user_id()
        if user_id is None: return "404"
        response_page = self._forms_response_page(user_id=user_id)
        return response_page


class PageWithPermitView(Page):
    """Страница с разрешением на ее просмотр"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)
    
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        user_id = self._get_user_id()
        if user_id is None or not self.__permit_view_page(user_id):
            return "404"
        response_page = self._forms_response_page(user_id=user_id)
        return response_page
    
    def __permit_view_page(self, user_id: int) -> bool:
        """Разрешение просмотра страницы."""
        page_uri = get_current_page_uri()
        permit = page_db.get_permit_view_page(user_id, page_uri)
        return permit


class PageAvailableWithSideMenu(PageAvailable):
    """Страница доступная с боковым меню"""

    def __init__(self, template: str):
        constructor = ConstructorPageTemplateWithSideMenu(template)
        super().__init__(constructor)


class PageAvailableWithoutSideMenu(PageAvailable):
    """Страница доступная без бокового меню"""

    def __init__(self, template: str):
        constructor = ConstructorPageTemplateWithoutSideMenu(template)
        super().__init__(constructor)


class PageWithPermitViewWithSideMenu(PageWithPermitView):
    """Страница с боковым меню с разрешением на ее просмотр """

    def __init__(self, template: str):
        constructor = ConstructorPageTemplateWithSideMenu(template)
        super().__init__(constructor)


class PageWithPermitViewWithoutSideMenu(PageWithPermitView):
    """Страница без бокового меню с разрешением на ее просмотр"""

    def __init__(self, template: str):
        constructor = ConstructorPageTemplateWithoutSideMenu(template)
        super().__init__(constructor)

#также можно создать страницу со своим конструктором и с добавкой данных