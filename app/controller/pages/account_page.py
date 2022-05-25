from .page import AppPage, ConstructorPageTemplate
from flask import typing as flaskTyping, redirect
from database import user_db
from typing import Dict


class AccountPage(AppPage):
    """Страница аккаунта пользователя (доступна всем пользователям)"""

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)

    def get_response_page(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ страницу."""
        if not self._authentication_user:
            return redirect("/", code=302)
        response_page = self._forms_response_page(
            account_data=self.__get_account_data()
        )
        return response_page

    def __get_account_data(self) -> Dict[str, str]:
        """Получает данные аккаунта пользователя."""
        user_id = self._authentication_user.id
        account_data = user_db.get_account_data(user_id)
        return {
            'last_name': account_data[0],
            'first_name': account_data[1],
            'patronymic': account_data[2],
            'email': account_data[3],
            'company': account_data[4]
        }
