from typing import Any, List, Dict, Union, Optional, Tuple
from service_layer.authentication import UserAuthenticationInfo, AuthenticationByCookies
from abc import ABC, abstractmethod
from flask import typing as flaskTyping
from .page_funcs import template_response, get_current_page_uri, get_cookie, add_cookie_session_to_response
from database import page_db, user_db

from typing import Type, TypeVar, Optional, Dict, Union, Tuple
from utilities.validations import Validation
from enum import Enum
from .page_funcs import success_response, error_response






class Authentication:
    """Аутентификация"""

    __user_authentication_info: UserAuthenticationInfo

    def __init__(self):
        self.__user_authentication_info = self.__authenticates_user() 
    
    def __authenticates_user(self) -> UserAuthenticationInfo:
        """Аутентифицирует пользователя."""
        cookie_session = get_cookie("Session")
        cookie_auth = get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth).get_user_authentication_info()
    
    def get_user_id(self) -> Optional[int]:
        """Получает id пользователя."""
        return self.__user_authentication_info.user_id
    
    def get_cookie_session(self) -> Optional[str]:
        """Получает куки сессии."""
        return self.__user_authentication_info.cookie_session


#Логика получения HTML страницы:
class ConstructorPageTemplate(ABC):
    """Базовый класс - Конструктор шаблона страницы"""

    _template: str

    def __init__(self, template):
        self._template = template

    @abstractmethod
    def creates(self, kwargs: Dict[str, Any]) -> flaskTyping.ResponseReturnValue:
        """Создает страницу."""
        raise NotImplementedError()


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
                'supplement': kwargs.get('supplement', None)
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


class Page(ABC, InterfaceAuthentication):
    """Базовый класс - Страница"""

    _constructor: ConstructorPageTemplate

    def __init__(self, constructor):
        self._constructor = constructor
        
    @abstractmethod
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        raise NotImplementedError()
        
    def _forms_response_page(self, **kwargs) -> flaskTyping.ResponseReturnValue:
        """Формирует ответ страницу."""
        response_page = self._constructor.creates(kwargs)
        add_cookie_session_to_response(
            response_page, 
            cookie_session = self.get_cookie_session()
        )
        return response_page


class PageAvailable(Page):
    """Страница доступная (разрешение на ее просмотр не требуется)."""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)
    
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        user_id = self.get_user_id()
        if user_id is None: return "404"
        response_page = self._forms_response_page(user_id=user_id)
        return response_page


class PageWithPermitView(Page):
    """Страница с разрешением на ее просмотр"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)
    
    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ."""
        user_id = self.get_user_id()
        if user_id is None or not self.__permit_view_page(user_id):
            return "404"
        response_page = self._forms_response_page(user_id=user_id)
        return response_page
    
    def __permit_view_page(self, user_id: int) -> bool:
        """Разрешение просмотра страницы."""
        page_uri = get_current_page_uri()
        permit = page_db.get_permit_view_page(user_id, page_uri)
        return permit


#Логика получения ответа от страницы:
class HandlerRequest(ABC):
	"""Базовый класс - Обработчик запроса"""

	_operation_error: Optional[int]

	def __init__(self):
		self._operation_error = None

	@abstractmethod
	def handle(self) -> Optional[Union[bool, Tuple[str]]]:
		"""Обрабатывает соответствующий запрос."""
		raise NotImplementedError()

	def _check_validation_value(self, value: str, validation: Validation, error_type: Enum):
		"""Проверяет значение на валидацию."""
		if not (result := validation(value).get_result()):
			self._set_operation_error(error_type)
		return result

	def _set_operation_error(self, error_type: Enum) -> None:
		"""Устанавливает ошибку операции."""
		self._operation_error = error_type.value

	def get_operation_error(self) -> Optional[int]:
		"""Получает ошибку операции."""
		return self._operation_error


Handler = TypeVar("Handler", bound=HandlerRequest)

class ResponseFromPage:
	"""Ответ от страницы"""

	__handler: Type[Handler]
	__request_data: Optional[Dict[str, str]]

	def __init__(self, handler, request_data):
		self.__handler = handler
		self.__request_data = request_data

	def get(self) -> flaskTyping.ResponseReturnValue:
		"""Получает ответ от страницы."""
		if self.__request_data is None:
			return error_response(code_error=2, type_error="app")
		handler = self.__handler(self.__request_data)
		response = handler.handle()
		if not response:
			code_error = handler.get_operation_error()
			return error_response(code_error, type_error="auth")
		return success_response(value=response)