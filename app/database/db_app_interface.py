from .db import SQLite


def get_side_menu_data(user_id: int) -> list[tuple]:
	"""Получает данные бокового меню."""
	with SQLite() as cursor:
		query = """
			SELECT
				items_out.side_menu_item_id as side_menu_item_id,
				items_out.side_menu_item_name as side_menu_item_name,
				items_out.side_menu_item_parent_id as side_menu_item_parent_id,
				items_out.page_id as side_menu_item_uri
			FROM side_menu_items as items_out
			WHERE EXISTS (
				SELECT DISTINCT
					items_inner.side_menu_item_parent_id
				FROM
					side_menu_items as items_inner
				JOIN
					permit_view_page as permit ON permit.page_id =
												items_inner.page_id
				WHERE
					permit.user_id = :user_id AND
					items_inner.side_menu_item_parent_id =
												items_out.side_menu_item_id
			)
			UNION
			SELECT
				items.side_menu_item_id as side_menu_item_id,
				items.side_menu_item_name as side_menu_item_name,
				items.side_menu_item_parent_id as side_menu_item_parent_id,
				p.page_uri as side_menu_item_uri
			FROM
				side_menu_items as items
			JOIN
				permit_view_page as permit ON permit.page_id = items.page_id
			JOIN
				pages as p ON p.page_id = items.page_id
			WHERE
				permit.user_id = :user_id
		"""
		cursor.execute(query, {'user_id': user_id})
		response_from_db = [row for row in cursor.fetchall()]
		return response_from_db

def get_permit_view_page(user_id: int, page_uri: str) -> bool:
	"""Получает разрешение на просмотр страницы."""
	with SQLite() as cursor:
		query = """
			SELECT
				(CASE
					WHEN COUNT(permit.user_id) = 1
					THEN True
					ELSE False
				END) as permit_user
			FROM permit_view_page as permit
			JOIN pages as p ON p.page_id = permit.page_id
			WHERE permit.user_id = :user_id and p.page_uri = :page_uri
		"""
		cursor.execute(query, {'user_id': user_id, 'page_uri': page_uri})
		response_from_db = bool(cursor.fetchone()[0])
		return response_from_db
