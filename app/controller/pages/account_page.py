from .page import AppPage, ConstructorPageTemplate
from flask import typing as flaskTyping, redirect
from database.models.user import Users


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

    def __get_account_data(self) -> dict[str, str]:
        """Получает данные аккаунта пользователя."""
        user_id = self._authentication_user.id
        user = Users.query.first()
        return {
            'last_name': user.last_name,
            'first_name': user.first_name,
            'patronymic': user.patronymic,
            'email': user.email,
            'company': user.company.name
        }
