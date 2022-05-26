from enum import Enum
from .handler import HandlerRequestWithCheckID
from typing import Optional
from models.account import AccountModel
from utilities.other import HashingData
from database import db_auth
from utilities.validations import ValidationPassword
from controller.service_layer.cookies import CreatorCookieAuth
from flask import typing as flaskTyping
from controller import common


class RequestDataErrors(Enum):
    """Ошибки в данных запроса"""
    FALSE_CURRENT_PASSWORD = 1


class ValidationErrors(Enum):
    """Ошибки валидации"""
    NOT_VALID_PASSWORD = 2


class HandlerRequestСhangePassword(HandlerRequestWithCheckID):
    """Обработчик запроса на изменение пароля"""

    __user_id: int
    __password: str
    __new_password: str
    __cookie_auth: Optional[str]
    __account_model: AccountModel

    def __init__(self, user_id, password, new_password):
        super().__init__()
        self.__user_id = user_id
        self.__password = password
        self.__new_password = new_password
        self.__cookie_auth = None
        self.__account_model = AccountModel()

    def handle(self) -> bool:
        """Обрабатывает запрос на изменение пароля."""
        if (not self._check_user_id(self.__user_id) or
            not self.__check_current_password() or
            not self.__check_new_password()):
            return False
        hashed_new_password = HashingData().calculate_hash(self.__new_password)
        self.__changes_password_in_db(hashed_new_password)
        self.__set_cookie_auth(hashed_new_password)
        return True

    def __check_current_password(self) -> bool:
        """Проверяет текущий пароль."""
        hashed_password = HashingData().calculate_hash(self.__password)
        result = db_auth.check_user_password(self.__user_id, hashed_password)
        if not result:
            self._set_handler_error(
                source=f"Текущий пароль: {self.__password}",
                type="FALSE_DATA",
                enum=RequestDataErrors.FALSE_CURRENT_PASSWORD
            )
        return result

    def __check_new_password(self) -> bool:
        """Проверяет новый пароль."""
        result = ValidationPassword(self.__new_password).get_result()
        if not result:
            self._set_handler_error(
                source=f"Новый пароль: {self.__new_password}",
                type="VALIDATION",
                enum=ValidationErrors.NOT_VALID_PASSWORD
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
        account_data = self.__account_model.get_data(self.__user_id)
        return account_data['email']

    def get_cookie_auth(self) -> Optional[str]:
        """Получает куки авторизации."""
        return self.__cookie_auth


class ResponseAboutChangePassword:
    """Ответ об изменении пароля"""

    __handler: HandlerRequestСhangePassword

    def __init__(self, handler):
        self.__handler = handler

    def get(self) -> flaskTyping.ResponseReturnValue:
        """Получает ответ."""
        result = self.__handler.handle()
        if not result:
            source_error, type_error, code_error = \
                                            self.__handler.get_handler_error()
            return common.error_response(source_error, type_error, code_error)
        response = common.make_json_response({}, 204)
        common.add_cookies_to_response(
            response,
            cookie_auth = self.__handler.get_cookie_auth()
        )
        return response
