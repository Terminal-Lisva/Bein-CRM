#from typing import *
#from main_objects.user_authentication import Authenticator
#from main_objects.user_interface import UserInterface
#from flask import render_template

pass
#class AppPage:
#    """Страница приложения"""
 
#    def __init__(self):
#        self.__authenticator = Authenticator()
    
#    def get_page(self):
#        """Получает страницу"""
#        info_user_authentication = self.__authenticator.authenticates_user() 
#        user_id = info_user_authentication["user_id"]
#        if user_id is None:
#            return "404"
#        data_tree_for_building_side_menu = UserInterface(user_id).get_data_tree_for_building_side_menu()
#        return render_template('app.html', data_tree=data_tree_for_building_side_menu)
        #надо не забыть поставить куки сессию в ответ!
        #cookie_session = info_user_authentication["cookie_session"]