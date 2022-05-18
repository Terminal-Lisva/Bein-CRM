from .page import PageWithSideMenu
from flask import typing as flaskTyping


class AppPage(PageWithSideMenu):
    """Страница приложения"""

    def __init__(self):
        super().__init__(template='app_page.html')

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        user_id = self._get_user_id()
        if user_id is None or not self._permit_view_page(user_id):
            return "404"
        response_page = self._forms_response_page(user_id)
        return response_page