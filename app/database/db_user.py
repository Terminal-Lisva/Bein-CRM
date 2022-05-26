from typing import Optional, Union, List, Tuple, Any
from .db import SQLite
from functools import singledispatch


@singledispatch
def get_user_data(arg: Optional[Union[str, int]])-> List[Tuple[Any, ...]]:
	"""Получает данные всех пользователей."""
	with SQLite() as cursor:
		query = """
			SELECT
				ud.user_id as id, ud.last_name as last_name,
				ud.first_name as first_name, ud.patronymic as patronymic,
				ud.email as email, ud.company_id as company_id,
				c.company_name as company_name
			FROM
				user_data as ud
			JOIN
				user_authorization as ua ON ua.user_id = ud.user_id
			JOIN
				company as c ON c.company_id = ud.company_id
		"""
		cursor.execute(query)
		return cursor.fetchall()

@get_user_data.register(str)
def _get_user_data_by_invitation_token(
	invitation_token: str) -> Optional[Tuple[Any, ...]]:
	"""Получает данные пользователя по токену приглашения."""
	with SQLite() as cursor:
		query = """
			SELECT
				ud.user_id as id, ud.last_name as last_name,
				ud.first_name as first_name, ud.patronymic as patronymic,
				ud.email as email, ud.company_id as company_id,
				c.company_name as company_name
			FROM
				user_data as ud
			JOIN
				user_authorization as ua ON ua.user_id = ud.user_id
			JOIN
				company as c ON c.company_id = ud.company_id
			JOIN
				invitation_tokens as it ON it.user_id = ud.user_id
			WHERE
				it.invitation_token = ?
		"""
		cursor.execute(query, (invitation_token,))
		response_from_db = cursor.fetchone()
		return response_from_db

@get_user_data.register(int)
def _get_user_data_by_user_id(user_id: int) -> Optional[Tuple[Any, ...]]:
	"""Получает данные пользователя по id."""
	with SQLite() as cursor:
		query = """
			SELECT
				ud.user_id as id, ud.last_name as last_name,
				ud.first_name as first_name, ud.patronymic as patronymic,
				ud.email as email, ud.company_id as company_id,
				c.company_name as company_name
			FROM
				user_data as ud
			JOIN
				user_authorization as ua ON ua.user_id = ud.user_id
			JOIN
				company as c ON c.company_id = ud.company_id
			WHERE
				ud.user_id = ?
		"""
		cursor.execute(query, (user_id,))
		response_from_db = cursor.fetchone()
		return response_from_db
