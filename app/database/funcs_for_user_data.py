from typing import Union, Optional, Tuple
from .database import SQLite
from functools import singledispatch


#ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ИЗ БД
@singledispatch
def get_user_data_from_db(arg: Union[str, int]) -> None:
	"""Получает данные пользователя из базы данных."""
	pass

@get_user_data_from_db.register(str)
def _get_user_data_by_invitation_token(token: str) -> Optional[tuple]:
	"""Получает данные пользователя по токену приглашения."""
	with SQLite() as cursor:
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
		""", (token,))
		return cursor.fetchone()

@get_user_data_from_db.register(int)
def _get_user_data_by_user_id(user_id: int) -> Optional[tuple]:
	"""Получает данные пользователя по id."""
	with SQLite() as cursor:
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

@singledispatch
def get_user_id_from_db(arg: Union[str, Tuple[str]]) -> Optional[int]:
	"""Получает id пользователя из базы данных."""
	pass

@get_user_id_from_db.register(str)
def _get_user_id_by_invitation_token(invitation_token: str) -> Optional[int]:
	"""Получает id пользователя по току приглашения."""
	with SQLite() as cursor:
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

@get_user_id_from_db.register(tuple)
def _get_user_id_by_email_and_password(args: Tuple[str]) -> Optional[int]:
	"""Получает id пользователя по емайлу и паролю."""
	email, hashed_password = args
	with SQLite() as cursor:
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

def check_user_authentication_in_db(user_id: int) -> bool:
	"""Проверяет аутентификацию пользователя в базе данных."""
	with SQLite() as cursor:
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
	
def add_user_authentication_to_db(user_id: int, hashed_password: str) -> None:
	"""Добавляет аутентификацию пользователя в базу данных."""
	with SQLite() as cursor:
		cursor.execute("""
			INSERT INTO user_authorization (user_id, hashed_password)
			VALUES (?, ?)
		""", (user_id, hashed_password,))
	
def remove_user_authentication_from_db(user_id: int) -> None:
	"""Удаляет аутентификацию пользователя из базы данных."""
	with SQLite() as cursor:
		cursor.execute("""
			DELETE FROM user_authorization WHERE user_id = ?
		""", (user_id,))

def get_user_fio_from_db(user_id: int) -> Optional[str]:
	"""Получает ФИО пользователя из базы данных."""
	with SQLite() as cursor:
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


#class DatabaseUserInterface():
#	"""База данных интерфейс пользователя"""
#
#	def get_user_side_menu_data(self, user_id: int) -> List[Tuple[Union[int, str]]]:
#		"""Получает данные бокового меню пользователя"""
#		with SQLite() as cursor:
#			cursor.execute("""
#				SELECT
#					items.*
#				FROM
#					side_menu_items as items
#				JOIN
#					side_menu_view_permit as permit 
#					ON permit.side_menu_item_id = items.side_menu_item_id
#				WHERE 
#					permit.user_id = ?
#			""", (user_id,))
#			response_from_database = [row for row in cursor.fetchall()]
#			return response_from_database