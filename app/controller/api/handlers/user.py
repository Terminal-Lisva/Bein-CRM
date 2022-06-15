from .handler import HandlerResult, Error, HandlerError
from abc import ABC
from utilities.validations import ValidationInvitationToken, ValidationPassword
from controller.api.errors import Errors
from database import db_auth
from typing import TypedDict
from database.models.user import Users
from controller.api import for_api
from utilities.other import (records_log_user_registration,
records_log_user_restorer, HashingData)


class Meta(TypedDict):
    href: str
    type: str


class DocumentUser(TypedDict):
    meta: Meta
    id: int
    last_name: str
    first_name: str
    patronymic: str
    company: Meta


class HandlerRequestActivationUser(ABC):
    """Обоработчик запроса изменения пользователя"""

    _token: str
    _password: str
    _handler_result: HandlerResult

    def __init__(self, token, password):
        self._token = token
        self._password = password
        self._handler_result = HandlerResult()

    def _check_request_data(self) -> bool:
        """Проверяет данные из запроса."""
        if not ValidationInvitationToken(self._token).get_result():
            message, status_code = Errors.NOT_VALID_TOKEN.value
            self._handler_result.error = Error(
                source=f"Токен приглашения: {self._token}",
                type=Errors.NOT_VALID_TOKEN.name,
                message=message
            )
            self._handler_result.status_code = status_code
            return False
        elif not ValidationPassword(self._password).get_result():
            message, status_code = Errors.NOT_VALID_PASSWORD.value
            self._handler_result.error = Error(
                source=f"Пароль: {self._password}",
                type=Errors.NOT_VALID_PASSWORD.name,
                message=message
            )
            self._handler_result.status_code = status_code
            return False
        return True

    def _get_user_id(self) -> int:
        """Получает id пользователя из базы данных.
        Если пользователь отсутствует в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        user_id = db_auth.get_user_id(self._token)
        if user_id is None:
            message, status_code = Errors.NO_TOKEN.value
            self._handler_result.error = Error(
                source=f"Токен приглашения: {self._token}",
                type=Errors.NO_TOKEN.name,
                message=message
            )
            self._handler_result.status_code = status_code
            raise HandlerError
        return user_id

    def _create_document(self, user_id: int) -> DocumentUser:
        """Создает документ."""
        user = Users.query.get(user_id)
        return DocumentUser(
            meta = Meta(
                href=for_api.make_href(path=f"/users/{user.id}"),
                type="app users"
            ),
            id = user.id,
            last_name = user.last_name,
            first_name = user.first_name,
            patronymic = user.patronymic,
            company = Meta(
                href=for_api.make_href(path=f"/company/{user.company_id}"),
                type="company"
            )
        )


class HandlerRequestAddUser(HandlerRequestActivationUser):
    """Обоработчик запроса на добавление пользователя"""

    def __init__(self, token, password):
        super().__init__(token, password)

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на регистрацию пользователя."""
        if not self._check_request_data():
            return self._handler_result
        try:
            user_id = self._get_user_id()
            self._add_user_to_db(user_id)
        except HandlerError:
            return self._handler_result
        records_log_user_registration(user_id)
        self._handler_result.document = self._create_document(user_id)
        self._handler_result.status_code = 201
        return self._handler_result

    def _add_user_to_db(self, user_id: int) -> None:
        """Добавляет пользователя в базу данных.
        Если пользователь уже имеется в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        if not db_auth.check_user_authentication(user_id):
            message, status_code = Errors.USER_IS_BD.value
            self._handler_result.error = Error(
                source=f"id: {user_id}",
                type=Errors.USER_IS_BD.name,
                message=message
            )
            self._handler_result.status_code = status_code
            raise HandlerError
        hashed_password = HashingData().calculate_hash(self._password)
        db_auth.add_user_authentication(user_id, hashed_password)


class HandlerRequestRestoreUser(HandlerRequestActivationUser):
    """Обработчик запроса на восстановление пользователя"""

    def __init__(self, token, password):
        super().__init__(token, password)

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на восстановление пароля."""
        if not self._check_request_data():
            return self._handler_result
        try:
            user_id = self._get_user_id()
            self._restores_user_to_db(user_id)
        except HandlerError:
            return self._handler_result
        records_log_user_restorer(user_id)
        document = self._create_document(user_id)
        return HandlerResult(document, status_code=201)

    def _restores_user_to_db(self, user_id: int) -> None:
        """Восстанавливает пользователя в базе данных.
        Если пользователя нет в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        if db_auth.check_user_authentication(user_id):
            message, status_code = Errors.USER_IS_NOT_BD.value
            self._handler_result.error = Error(
                source=f"id: {user_id}",
                type=Errors.USER_IS_NOT_BD.name,
                message=message
            )
            self._handler_result.status_code = status_code
        db_auth.remove_user_authentication(user_id)
        hashed_password = HashingData().calculate_hash(self._password)
        db_auth.add_user_authentication(user_id, hashed_password)
