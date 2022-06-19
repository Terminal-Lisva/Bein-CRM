from utilities.other import HashingData
from pydantic import BaseModel
from .handler import HandlerPostRequest, HandlerResult, HandlerError
from controller.api.errors import Errors
from database import db_auth
from utilities.validations import ValidationPassword
from database.models.user import User
from controller.service_layer.cookies import CreatorCookieAuth


def _get_hash_password(password: str) -> str:
    """Получает хэш пароля."""
    return HashingData().calculate_hash(password)


class ModelСhangePassword(BaseModel):
    password: str
    new_password: str


class HandlerRequestСhangePassword(HandlerPostRequest):
    """Обработчик запроса на изменение пароля"""

    _user_id: int
    _model_data: ModelСhangePassword
    _cookie_auth: str | None

    def __init__(self, user_id, data_from_request):
        super().__init__(data_from_request, model=ModelСhangePassword)
        self._user_id = user_id
        self._model_data = self._get_model_data_post_request()
        self._cookie_auth = None

    def handle(self) -> HandlerResult:
        """Обрабатывает запрос на изменение пароля."""
        try:
            self._check_user_id()
            self._check_cur_password()
            self._check_new_password()
        except HandlerError:
            return self._handler_result
        hash_new_password = _get_hash_password(self._model_data.new_password)
        self._change_password_in_db(hash_new_password)
        self._set_cookie_auth(hash_new_password)
        self._handler_result.document = {"message": "Пароль успешно изменен"}
        self._handler_result.status_code = 201
        return self._result

    def _check_user_id(self) -> None:
        """Проверяет аутентификацию пользователя.
        Сверяет входную ID пользователя с ID из аутентификации."""
        if (not self._check_authentication_user() or
        self._user_id != self._authentication_user.user_id):
            self._set_error_in_handler_result(
                source="",
                error=Errors.NO_PERMISSION_RESOURCE
            )
            raise HandlerError

    def _check_cur_password(self) -> None:
        """Проверяет текущий пароль."""
        hashed_password = _get_hash_password(self._model_data.password)
        result = db_auth.check_user_password(self._user_id, hashed_password)
        if not result:
            self._set_error_in_handler_result(
                source=f"Текущий пароль: {self._model_data.password}",
                error=Errors.FALSE_PASSWORD
            )
            raise HandlerError

    def _check_new_password(self) -> None:
        """Проверяет новый пароль."""
        result = ValidationPassword(self._model_data.new_password).get_result()
        if not result:
            self._set_error_in_handler_result(
                source=f"Новый пароль: {self._model_data.new_password}",
                error=Errors.NOT_VALID_PASSWORD
            )
            raise HandlerError

    def _change_password_in_db(self, hash_new_password: str) -> None:
        """Изменяет пароль в базе данных."""
        db_auth.remove_user_authentication(self._user_id)
        db_auth.add_user_authentication(self._user_id, hash_new_password)

    def _set_cookie_auth(self, hash_new_password: str) -> None:
        """Устанавливает куки авторизации."""
        user = User.query.get(self._user_id)
        self._cookie_auth = CreatorCookieAuth().creates(
            email=user.email,
            hashed_password=hash_new_password
        )

    def get_cookie_auth(self) -> str | None:
        """Получает куки авторизации."""
        return self._cookie_auth
