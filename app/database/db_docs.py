from .db import SQLite, sqlite3
from typing import TypedDict


class DataForAdd(TypedDict):
	id_bpm: int
	id_type_doc: int
	id_company: int
	id_creator: int


ErrorAddingCodeDoc = sqlite3.IntegrityError


def add_code_doc(data: DataForAdd) -> int:
	"""Добавляет код документа."""
	with SQLite() as cursor:
		cursor.execute("PRAGMA foreign_keys = ON")
		query = """
			INSERT INTO code_documents
			(id_bpm, id_type_doc, id_company, number, id_creator)
			VALUES (
				:id_bpm,
				:id_type_doc,
				:id_company,
				(
					SELECT count(number)+1
					FROM code_documents
					WHERE
						id_bpm = :id_bpm and
						id_type_doc = :id_type_doc and
						id_company = :id_company
				),
				:id_creator
			)
		"""
		cursor.execute(query, data)
		cursor.execute("SELECT last_insert_rowid()")
		return cursor.fetchone()[0]
