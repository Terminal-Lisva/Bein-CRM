from .page import AppPage, ConstructorPageTemplate
from flask import typing as flaskTyping, redirect
from models.account import AccountModel
from typing import Dict


class AccountPage(AppPage):
    """Страница аккаунта пользователя (доступна всем пользователям)"""

    __account_model: AccountModel

    def __init__(self, constructor: ConstructorPageTemplate):
        super().__init__(constructor)
        self.__account_model = AccountModel()

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
        account_data = self.__account_model.get_data(user_id)
        return {
            'last_name': account_data['last_name'],
            'first_name': account_data['first_name'],
            'patronymic': account_data['patronymic'],
            'email': account_data['email'],
            'company': account_data['company']['name']
        }
