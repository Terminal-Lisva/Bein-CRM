from .handler import HandlerRequestWithCheckID, HandlerResult
from utilities.other import HashingData
from database import db_auth
from controller.api.errors import Errors
from utilities.validations import ValidationPassword
from database.models.user import Users
from controller.service_layer.cookies import CreatorCookieAuth
from flask import typing as flaskTyping
from controller import common


class HandlerRequestСhangePassword(HandlerRequestWithCheckID):
    """Обработчик запроса на изменение пароля"""

    __user_id: int
    __password: str
    __new_password: str
    __cookie_auth: str | None

    def __init__(self, user_id, password, new_password):
        super().__init__()
        self.__user_id = user_id
        self.__password = password
        self.__new_password = new_password
        self.__cookie_auth = None

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на изменение пароля."""
        if (not self._check_user_id(self.__user_id) or
            not self.__check_current_password() or
            not self.__check_new_password()):
            return self._result
        hashed_new_password = HashingData().calculate_hash(self.__new_password)
        self.__changes_password_in_db(hashed_new_password)
        self.__set_cookie_auth(hashed_new_password)
        self._result.document = {"message": "Пароль успешно изменен"}
        self._result.status_code = 201
        return self._result

    def __check_current_password(self) -> bool:
        """Проверяет текущий пароль."""
        hashed_password = HashingData().calculate_hash(self.__password)
        result = db_auth.check_user_password(self.__user_id, hashed_password)
        if not result:
            self._set_error_in_handler_result(
                source=f"Текущий пароль: {self.__password}",
                error=Errors.FALSE_PASSWORD
            )
        return result

    def __check_new_password(self) -> bool:
        """Проверяет новый пароль."""
        result = ValidationPassword(self.__new_password).get_result()
        if not result:
            self._set_error_in_handler_result(
                source=f"Новый пароль: {self.__new_password}",
                error=Errors.NOT_VALID_PASSWORD
            )
        return result

    def __changes_password_in_db(self, hashed_password: str) -> None:
        """Изменяет пароль в базе данных."""
        db_auth.remove_user_authentication(self.__user_id)
        db_auth.add_user_authentication(self.__user_id, hashed_password)

    def __set_cookie_auth(self, hashed_password: str) -> None:
        """Устанавливает куки авторизации."""
        email = self.__get_email()
        self.__cookie_auth = CreatorCookieAuth().creates(email, hashed_password)

    def __get_email(self) -> str:
        """Получает email пользователя."""
        user = Users.query.get(self.__user_id)
        return user.email

    def get_cookie_auth(self) -> str | None:
        """Получает куки авторизации."""
        return self.__cookie_auth
