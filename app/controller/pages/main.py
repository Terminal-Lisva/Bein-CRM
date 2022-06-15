from .page import AppPage, ConstructorPageTemplate
from flask import typing as flaskTyping, redirect


class MainPage(AppPage):
    """Главная страница приложения (доступна всем пользователям)"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        if not self._authentication_user:
            return redirect("/", code=302)
        response_page = self._forms_response_page()
        return response_page
