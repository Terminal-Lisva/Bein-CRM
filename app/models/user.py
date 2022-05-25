from typing import TypedDict, Optional, Union, List, Tuple, Any
from database import user_db
from flask import request


class DataDict(TypedDict):
    id: int
    registration: bool
    last_name: str
    first_name: str
    patrotymic: str
    email: str
    company: str

#ORM пока не используется!
class UserModel:
    """Модель пользователя"""

    def get_data(
        self,
        arg: Optional[Union[str, int]]
        ) -> Optional[Union[DataDict, List[DataDict]]]:
        """Получает данные пользователя(ей)."""
        data_from_db = user_db.get_user_data(arg)
        if isinstance(data_from_db, tuple):
            return self.__forms_data(data_from_db)
        elif isinstance(data_from_db, list):
            return [self.__forms_data(row) for row in data_from_db]
        else:
            return None

    def __forms_data(self, data_from_db: Tuple[Any, ...]) -> DataDict:
        """Формирует данные."""
        return {
            "id": data_from_db[0],
            "registration": bool(data_from_db[1]),
            "last_name": data_from_db[2],
            "first_name": data_from_db[3],
            "patrotymic": data_from_db[4],
            "email": data_from_db[5],
            "company":
                f"{request.url_root}api/1.1/company/{data_from_db[6]}"
        }
