from .page import Page, ConstructorPageTemplateWithSideMenu
from flask import typing as flaskTyping
from .page_funcs import add_cookie_session_to_response


class AppPage(Page):
    """Страница приложения"""

    def __init__(self):
        constructor = ConstructorPageTemplateWithSideMenu('app_page.html')
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        user_id = self._get_user_id()
        if user_id is None or not self._permit_view_page(user_id):
            return "404"
        response_page = self._constructor.creates(user_id, self._page_uri)
        add_cookie_session_to_response(
            response_page, 
            cookie_session = self._get_cookie_session()
        )
        return response_page