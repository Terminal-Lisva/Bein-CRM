from typing import *
from database.database import DatabaseUserInterface


class UserInterface:
    """Интерфейс пользователя"""

    def __init__(self, user_id: int):
        self.__user_id = user_id
        self.__db = DatabaseUserInterface()
    
    def get_data_for_building_side_menu(self) -> List[Dict[str, Union[str, list]]]:
        """Получает данные для построения бокового меню"""
        user_side_menu_data = self.__db.get_user_side_menu_data(self.__user_id)
        data_for_building_side_menu = []
        def creates_tree(l, parent_id):
            for row in user_side_menu_data:
                item_id = row[0]
                item_name = row[1]
                parent_item_id = row[2]
                item_href = row[3]
                if parent_item_id == parent_id:
                    l.append({
                        'name': item_name, 
                        'href': item_href,
                        'children': []
                    })
                    creates_tree(l[-1]['children'], item_id)
        creates_tree(l=data_for_building_side_menu, parent_id=0)
        return data_for_building_side_menu
    
    def get_permit_view_X_page(self):
        pass
        


