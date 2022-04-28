from typing import *
from functools import singledispatch
import sqlite3


class Database:
	"""База данных"""
	
	__path = "./database/web_kard.db"

	def _create_connect(self):
		return sqlite3.connect(Database.__path)


class DatabaseUsers(Database):
	"""База данных пользователей"""

	def __init__(self):
		"""Создаем перегрузку методов"""
		self.get_user_data = singledispatch(self.get_user_data)
		self.get_user_data.register(str, self.__get_user_data_from_database_by_invitation_token)
		self.get_user_data.register(int, self.__get_user_data_from_database_by_id)
		self.get_user_id = singledispatch(self.get_user_id)
		self.get_user_id.register(str, self.__get_user_id_by_invitation_token)
		self.get_user_id.register(tuple, self.__get_user_id_by_email_and_password)

	def get_user_data(self, arg: Union[str, int]) -> None:
		"""Получает данные пользователя"""
		return
	
	def __get_user_data_from_database_by_invitation_token(self, invitation_token: str) -> Optional[tuple]:
		"""Получает данные пользователя из базы данных по токену приглашения"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT 
                    ud.last_name as last_name, ud.first_name as first_name, ud.patronymic as patronymic, 
                    ud.email as email, c.company_name as company_name
                FROM
                    user_data as ud
                LEFT JOIN 
                    company as c ON c.company_id = ud.company_id
                LEFT JOIN 
                    invitation_tokens as it ON it.user_id = ud.user_id
                WHERE
                    it.invitation_token = ?
			""", (invitation_token,))
			return cursor.fetchone()

	def __get_user_data_from_database_by_id(self, user_id: int) -> Optional[tuple]:
		"""Получает данные пользователя из базы данных по id"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT 
                    ud.last_name as last_name, ud.first_name as first_name, ud.patronymic as patronymic, 
                    ud.email as email, c.company_name as company_name
                FROM
                    user_data as ud
                LEFT JOIN 
                    company as c ON c.company_id = ud.company_id
                LEFT JOIN 
                    invitation_tokens as it ON it.user_id = ud.user_id
                WHERE
                    ud.user_id = ?
			""", (user_id,))
			return cursor.fetchone()
	
	def get_user_id(self, arg: Union[str, Tuple[str]]) -> Optional[int]:
		"""Получает id пользователя"""
		print(0)
		return
	
	def __get_user_id_by_invitation_token(self, invitation_token: str) -> Optional[int]:
		"""Получает id пользователя по току приглашения"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT 
					ud.user_id as user_id
				FROM 
					user_data as ud
				JOIN 
					invitation_tokens as it ON it.user_id = ud.user_id
				WHERE it.invitation_token = ?
			""", (invitation_token,))
			response_from_database = cursor.fetchone()
			return response_from_database[0] if response_from_database is not None else None
	
	def __get_user_id_by_email_and_password(self, args: Tuple[str]) -> Optional[int]:
		"""Получает id пользователя по емайлу и паролю"""
		email, hashed_password = args
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT
					ud.user_id as user_id
				FROM
					user_data as ud
				JOIN 
					user_authorization as ua ON ua.user_id = ud.user_id
				WHERE
					ud.email = ? AND ua.hashed_password = ?
			""", (email, hashed_password,))
			response_from_database = cursor.fetchone()
			return response_from_database[0] if response_from_database is not None else None

	def check_user_authentication(self, user_id: int) -> bool:
		"""Проверяет аутентификацию пользователя"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT 
					(CASE 
						WHEN COUNT(user_id) = 1
						THEN False
						ELSE True
					END) as check_user
				FROM user_authorization as ua
				WHERE ua.user_id = ?
			""", (user_id,))
			return bool(cursor.fetchone()[0])
	
	def add_user_authentication(self, user_id: int, hashed_password: str) -> None:
		"""Добавляет аутентификацию пользователя"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				INSERT INTO user_authorization (user_id, hashed_password)
				VALUES (?, ?)
			""", (user_id, hashed_password,))
	
	def remove_user_authentication(self, user_id: int) -> None:
		"""Удаляет аутентификацию пользователя"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				DELETE FROM user_authorization WHERE user_id = ?
			""", (user_id,))

	def get_user_fio(self, user_id: int) -> Optional[str]:
		"""Получает ФИО пользователя"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT 
					last_name || ' ' || first_name || ' ' || patronymic 
				FROM 
					user_data 
				WHERE 
					user_id = ?
			""", (user_id,))
			response_from_database = cursor.fetchone()
			return response_from_database[0] if response_from_database is not None else None


class DatabaseUserInterface(Database):
	"""База данных интерфейс пользователя"""

	def get_user_side_menu_data(self, user_id: int) -> List[Tuple[Union[int, str]]]:
		"""Получает данные бокового меню пользователя"""
		with self._create_connect() as conn:
			cursor = conn.cursor()
			cursor.execute("""
				SELECT
					items.*
				FROM
					side_menu_items as items
				JOIN
					side_menu_view_permit as permit 
					ON permit.side_menu_item_id = items.side_menu_item_id
				WHERE 
					permit.user_id = ?
			""", (user_id,))
			response_from_database = [row for row in cursor.fetchall()]
			return response_from_database



