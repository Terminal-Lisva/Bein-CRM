from dataclasses import dataclass, field
from typing import Optional
from .authentication import Authentication, AuthenticationByCookies
from controller import common


@dataclass
class UserAuthenticationInfo:
    """Информация об аутентификации пользователя"""

    id: Optional[int] = field(init=False)
    cookie_session: Optional[str] = field(init=False)

    def __post_init__(self):
        authentication = self.__get_authentication()
        self.id = authentication.authenticates_user()
        self.cookie_session = authentication.get_cookie_session()

    def __get_authentication(self) -> Authentication:
        """Получает аутентификацию."""
        cookie_session = common.get_cookie("Session")
        cookie_auth = common.get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth)

    def __bool__(self) -> bool:
        """Проверка на наличие пользователя."""
        return self.id is not None
