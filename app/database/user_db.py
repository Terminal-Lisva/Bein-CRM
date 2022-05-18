from typing import Union, Optional, Tuple
from .db import SQLite
from functools import singledispatch


#ФУНКЦИИ ДЛЯ ПОЛУЧЕНИЯ ДАННЫХ ПОЛЬЗОВАТЕЛЯ ИЗ БД
@singledispatch
def get_user_data(arg: Union[str, int]) -> Optional[tuple]:
	"""Получает данные пользователя."""
	pass

@get_user_data.register(str)
def _get_user_data_by_invitation_token(token: str) -> Optional[tuple]:
	"""Получает данные пользователя по токену приглашения."""
	with SQLite() as cursor:
		query = """
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
		"""
		cursor.execute(query, (token,))
		response_from_db = cursor.fetchone()
		return response_from_db

@get_user_data.register(int)
def _get_user_data_by_user_id(user_id: int) -> Optional[tuple]:
	"""Получает данные пользователя по id."""
	with SQLite() as cursor:
		query = """
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
		"""
		cursor.execute(query, (user_id,))
		response_from_db = cursor.fetchone()
		return response_from_db

@singledispatch
def get_user_id(arg: Union[str, Tuple[str]]) -> Optional[int]:
	"""Получает id пользователя."""
	pass

@get_user_id.register(str)
def _get_user_id_by_invitation_token(invitation_token: str) -> Optional[int]:
	"""Получает id пользователя по току приглашения."""
	with SQLite() as cursor:
		query = """
			SELECT 
				ud.user_id as user_id
			FROM 
				user_data as ud
			JOIN 
				invitation_tokens as it ON it.user_id = ud.user_id
			WHERE it.invitation_token = ?
		"""
		cursor.execute(query, (invitation_token,))
		response_from_db = cursor.fetchone()
		return response_from_db[0] if response_from_db is not None else None

@get_user_id.register(tuple)
def _get_user_id_by_email_and_password(args: Tuple[str]) -> Optional[int]:
	"""Получает id пользователя по емайлу и паролю."""
	email, hashed_password = args
	with SQLite() as cursor:
		query = """
			SELECT
				ud.user_id as user_id
			FROM
				user_data as ud
			JOIN 
				user_authorization as ua ON ua.user_id = ud.user_id
			WHERE
				ud.email = :email AND ua.hashed_password = :hashed_password
		"""
		cursor.execute(query, {'email': email, 'hashed_password': hashed_password})
		response_from_db = cursor.fetchone()
		return response_from_db[0] if response_from_db is not None else None

def check_user_authentication(user_id: int) -> bool:
	"""Проверяет аутентификацию пользователя."""
	with SQLite() as cursor:
		query = """
			SELECT 
				(CASE 
					WHEN COUNT(user_id) = 1
					THEN False
					ELSE True
				END) as check_user
			FROM user_authorization as ua
			WHERE ua.user_id = ?
		"""
		cursor.execute(query, (user_id,))
		response_from_db = bool(cursor.fetchone()[0])
		return response_from_db
	
def add_user_authentication(user_id: int, hashed_password: str) -> None:
	"""Добавляет аутентификацию пользователя."""
	with SQLite() as cursor:
		query = """
			INSERT INTO user_authorization (user_id, hashed_password)
			VALUES (:user_id, :hashed_password)
		"""
		cursor.execute(query, {'user_id': user_id, 'hashed_password': hashed_password})
	
def remove_user_authentication(user_id: int) -> None:
	"""Удаляет аутентификацию пользователя."""
	with SQLite() as cursor:
		query = """
			DELETE FROM user_authorization WHERE user_id = ?
		"""
		cursor.execute(query, (user_id,))

def get_user_fio(user_id: int) -> Optional[str]:
	"""Получает ФИО пользователя."""
	with SQLite() as cursor:
		query = """
			SELECT 
				last_name || ' ' || first_name || ' ' || patronymic 
			FROM 
				user_data 
			WHERE 
				user_id = ?
		"""
		cursor.execute(query, (user_id,))
		response_from_db = cursor.fetchone()
		return response_from_db[0] if response_from_db is not None else None