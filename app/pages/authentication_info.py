from dataclasses import dataclass, field
from typing import Optional
from service_layer.authentication import Authentication, AuthenticationByCookies
from .page_funcs import get_cookie


@dataclass
class AuthenticationInfo:

    user_id: Optional[int] = field(init=False)
    cookie_session: Optional[str] = field(init=False)

    def __post_init__(self):
        authentication = self.__get_authentication() 
        self.user_id = authentication.authenticates_user()
        self.cookie_session = authentication.get_cookie_session()  
    
    def __get_authentication(self) -> Authentication:
        """Получает аутентификацию."""
        cookie_session = get_cookie("Session")
        cookie_auth = get_cookie("Auth")
        return AuthenticationByCookies(cookie_session, cookie_auth)