from dataclasses import dataclass, field
from typing import Optional, Tuple
from .authentication import Authentication, AuthenticationByCookies
from pages.page_funcs import get_cookie
from database import user_db


@dataclass
class User:
    """Пользователь"""

    id: Optional[int] = field(init=False)
    cookie_session: Optional[str] = field(init=False)

    def __post_init__(self):
        authentication = self.__get_authentication()
        self.id = authentication.authenticates_user()
        self.cookie_session = authentication.get_cookie_session()

    def __get_authentication(self) -> Authentication:
        """Получает аутентификацию."""
        cookie_session = get_cookie("Session")
        cookie_auth = get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth)

    def get_data(self) -> Optional[Tuple[str]]:
        """Получает данные пользователя."""
        if self.id is None:
            return None
        return user_db.get_user_data(self.id)

    def __bool__(self) -> bool:
        """Проверка наличия пользователя."""
        return self.id is not None
