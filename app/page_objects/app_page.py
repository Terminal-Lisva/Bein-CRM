from typing import *
from main_objects.authenticator import Authenticator
from utilities.other import SuccessResponse


class AppPage:
    """Страница приложения"""
 
    def __init__(self):
        self.__authenticator = Authenticator()
        #self.__inter
        self.__success_response = SuccessResponse()
    
    def get_app_page(self):
        """Получает страницу приложения"""
        info_user_authentication = self.__authenticator.authenticates_user() 
        user_id = info_user_authentication["user_id"]
        if user_id is None:
            return "404"
        
        #надо не забыть поставить куки сессию в ответ!
        cookie_session = info_user_authentication["cookie_session"]