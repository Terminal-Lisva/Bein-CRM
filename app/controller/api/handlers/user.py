from pydantic import BaseModel
from typing import TypedDict
from .handler import HandlerPostRequest, HandlerResult, HandlerError
from abc import ABC, abstractmethod
from utilities.validations import ValidationInvitationToken, ValidationPassword
from controller.api.errors import Errors
from database import db_auth
from database.models.user import User
from controller.api import for_api
from utilities.other import (records_log_user_registration,
records_log_user_restorer, HashingData)


class ModelActivationUser(BaseModel):
    token: str
    password: str


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


class HandlerRequestActivationUser(HandlerPostRequest, ABC):
    """Обоработчик запроса на активацию пользователя"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request, model=ModelActivationUser)

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на активацию пользователя."""
        try:
            model_data = self._get_model_data_post_request()
            self._check_model_data(model_data)
            user_id = self._get_user_id(model_data)
            self._make_appeal_to_db(user_id, model_data)
        except HandlerError:
            return self._handler_result
        orm_model = self._get_orm_model(user_id)
        self._handler_result.document = self._create_document(orm_model)
        self._handler_result.status_code = 201
        return self._handler_result

    def _check_model_data(self, model_data: ModelActivationUser) -> None:
        """Проверяет модель данных."""
        if not ValidationInvitationToken(model_data.token).get_result():
            self._set_error_in_handler_result(
                source=f"Токен приглашения: {model_data.token}",
                error=Errors.NOT_VALID_TOKEN
            )
            raise HandlerError
        elif not ValidationPassword(model_data.password).get_result():
            self._set_error_in_handler_result(
                source=f"Пароль: {model_data.password}",
                error=Errors.NOT_VALID_PASSWORD
            )
            raise HandlerError

    def _get_user_id(self, model_data: ModelActivationUser) -> int:
        """Получает id пользователя из базы данных.
        Если пользователь отсутствует в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        user_id = db_auth.get_user_id(model_data.token)
        if user_id is None:
            self._set_error_in_handler_result(
                source=f"Токен приглашения: {model_data.token}",
                error=Errors.NO_TOKEN
            )
            raise HandlerError
        return user_id

    @abstractmethod
    def _make_appeal_to_db(
        self, user_id: int, model_data: ModelActivationUser) -> None:
        """Делает обращение к БД."""
        raise NotImplementedError()

    def _get_orm_model(self, user_id: int) -> User:
        """Получает ORM модель."""
        orm_model = User.query.get(user_id)

    def _create_document(self, orm_model: User) -> DocumentUser:
        """Создает документ."""
        return DocumentUser(
            meta=Meta(
                href=for_api.make_href(path=f"/users/{orm_model.id}"),
                type="app users"
            ),
            id=orm_model.id,
            last_name=orm_model.last_name,
            first_name=orm_model.first_name,
            patronymic=orm_model.patronymic,
            company=Meta(
                href=for_api.make_href(path=f"/company/{orm_model.company_id}"),
                type="company"
            )
        )


class HandlerRequestAddUser(HandlerRequestActivationUser):
    """Обоработчик запроса на добавление пользователя"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request)

    def _make_appeal_to_db(
        self, user_id: int, model_data: ModelActivationUser) -> None:
        """Добавляет пользователя в базу данных.
        Если пользователь уже имеется в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        if not db_auth.check_user_authentication(user_id):
            self._set_error_in_handler_result(
                source=f"id: {user_id}",
                error=Errors.USER_IS_BD
            )
            raise HandlerError
        hashed_password = HashingData().calculate_hash(model_data.password)
        db_auth.add_user_authentication(user_id, hashed_password)
        records_log_user_registration(user_id)


class HandlerRequestRestoreUser(HandlerRequestActivationUser):
    """Обработчик запроса на восстановление пользователя"""

    def __init__(self, data_from_request):
        super().__init__(data_from_request)

    def _make_appeal_to_db(
        self, user_id: int, model_data: ModelActivationUser) -> None:
        """Восстанавливает пользователя в базе данных.
        Если пользователя нет в базе данных
        устанавливает соответствующую ошибку операции и вызывает исключение."""
        if db_auth.check_user_authentication(user_id):
            self._set_error_in_handler_result(
                source=f"id: {user_id}",
                error=Errors.USER_IS_NOT_BD
            )
            raise HandlerError
        db_auth.remove_user_authentication(user_id)
        hashed_password = HashingData().calculate_hash(model_data.password)
        db_auth.add_user_authentication(user_id, hashed_password)
        records_log_user_restorer(user_id)
