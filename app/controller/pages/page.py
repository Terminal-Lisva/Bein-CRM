from abc import ABC, abstractmethod
from flask import typing as flaskTyping, request, redirect
from controller import common
from controller.service_layer.authentication_info import UserAuthenticationInfo
from typing import Dict, Any, List
from models.user import UserModel
from database import page_db, user_db


#Логика получения HTML страницы:
class ConstructorPageTemplate(ABC):
    """Базовый класс - Конструктор шаблона страницы приложения"""

    _template: str

    def __init__(self, template):
        self._template = template

    @abstractmethod
    def creates(
        self,
        user_id: int,
        supplement: Dict[str, Any]) -> flaskTyping.ResponseReturnValue:
        """Создает страницу."""
        raise NotImplementedError()


class ConstructorPageTemplateWithSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы с боковым меню"""

    def __init__(self, template):
        super().__init__(template)

    def creates(
        self,
        user_id: int,
        supplement: Dict[str, Any]) -> flaskTyping.ResponseReturnValue:
        """Создает страницу с боковым меню.
        У пользователей разная видимость бокового меню."""
        side_menu_data = self.__get_tree_side_menu_data(user_id)
        title_data = self.__get_title_data(user_id)
        page = common.template_response(
            self._template,
            data = {
                'side_menu_data': side_menu_data,
                'title_data': title_data,
                'supplement': supplement
            }
        )
        return page

    def __get_tree_side_menu_data(self, user_id: int) -> List[dict]:
        """Получает дерево данных бокового меню пользователя."""
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

    def __get_title_data(self, user_id: int) -> Dict[str, str]:
        """Получает данные необходимые для построения заголовка."""
        data_from_db = user_db.get_user_data(user_id)
        return {"email": data_from_db[5], "last_name": data_from_db[2]}


class ConstructorPageTemplateWithoutSideMenu(ConstructorPageTemplate):
    """Конструктор шаблона страницы без бокового меню"""
    pass


class AppPage(ABC):
    """Базовый класс - Страница. Необходима аутентификация пользователя"""

    _constructor: ConstructorPageTemplate
    _authentication_user: UserAuthenticationInfo

    def __init__(self, constructor):
        self._constructor = constructor
        self._authentication_user = UserAuthenticationInfo()

    @abstractmethod
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        raise NotImplementedError()

    def _forms_response_page(self, **kwargs) -> flaskTyping.ResponseReturnValue:
        """Формирует ответ страницу."""
        response_page = self._constructor.creates(
            user_id=self._authentication_user.id,
            supplement=kwargs
        )
        common.add_cookies_to_response(
            response_page,
            cookie_session = self._authentication_user.cookie_session
        )
        return response_page


class PageWithPermitView(AppPage):
    """Страница с разрешением на ее просмотр. Пользователям доступны внутри
    приложения не все страницы"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ."""
        if not self._authentication_user:
            return redirect("/", code=302)
        elif not self.__permit_view_page():
            return "404"
        response_page = self._forms_response_page()
        return response_page

    def __permit_view_page(self) -> bool:
        """Разрешение просмотра страницы."""
        page_uri = request.path
        permit = page_db.get_permit_view_page(
            self._authentication_user.id, page_uri)
        return permit


class PageAvailable(AppPage):
    """Страница доступная всем (разрешение на ее просмотр не требуется)"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        if not self._authentication_user:
            return redirect("/", code=302)
        response_page = self._forms_response_page()
        return response_page
