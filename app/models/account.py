from typing import TypedDict, Dict, Union, Any
from database import db_user


class AccountDataDict(TypedDict):
    last_name: str
    first_name: str
    patrotymic: str
    email: str
    company: Dict[str, Union[int, str]]


class AccountModel:
    """Модель аккаунт пользователя"""

    def get_data(self, user_id: int) -> Dict[str, Any]: #->AccountDataDict
        """Получает данные аккаунта пользователя."""
        data_from_db = db_user.get_user_data(user_id)
        return {
            "last_name": data_from_db[1],
            "first_name": data_from_db[2],
            "patronymic": data_from_db[3],
            "email": data_from_db[4],
            "company": {"id": data_from_db[5], "name": data_from_db[6]},
        }
