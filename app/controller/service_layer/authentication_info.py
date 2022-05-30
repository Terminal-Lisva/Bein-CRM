from dataclasses import dataclass, field
from .authentication import AuthenticationByCookies
from controller import common


@dataclass
class UserAuthenticationInfo:
    """Информация об аутентификации пользователя"""

    user_id: int | None = field(init=False)
    cookie_session: str | None = field(init=False)

    def __post_init__(self):
        authentication = self.__get_authentication()
        self.user_id = authentication.authenticates_user()
        self.cookie_session = authentication.get_cookie_session()

    def __get_authentication(self) -> int | None:
        """Получает аутентификацию."""
        cookie_session = common.get_cookie("Session")
        cookie_auth = common.get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth)

    def __bool__(self) -> bool:
        """Проверка на наличие пользователя."""
        return self.user_id is not None
