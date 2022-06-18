from .db import SQLite, sqlite3
from typing import TypedDict, Literal
from datetime import date


class DataForAddCodeDoc(TypedDict):
	id_bpm: int
	id_type_doc: int
	id_company: int
	id_creator: int

def add_code_doc(data: DataForAddCodeDoc) -> int:
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


def del_code_doc(id_code_doc: int) -> None:
	with SQLite() as cursor:
		query = """
			DELETE FROM code_documents WHERE id = ?
		"""
		cursor.execute(query, (id_code_doc,))


class DataForAddDoc(TypedDict):
	id_code_doc: int
	name: str
	date_start: date
	date_finish: date
	id_responsible: int
	id_creator: int

def add_doc(data: DataForAddDoc) -> int:
	"""Добавляет документ."""
	with SQLite() as cursor:
		cursor.execute("PRAGMA foreign_keys = ON")
		cursor.execute("""
			INSERT INTO documents (
				id_code_doc, name, date_start, date_finish,
				id_responsible, id_creator
			)
			VALUES (
				:id_code_doc,
				:name,
				:date_start,
				:date_finish,
				:id_responsible,
				:id_creator
			)
		""", data)
		cursor.execute("""
			UPDATE code_documents
			SET used = 1
			WHERE id = :id_code_doc
		""", data)
		cursor.execute("SELECT last_insert_rowid()")
		return cursor.fetchone()[0]


class DataForUpdateDoc(TypedDict):
	id_doc: int
	date_start: date
	date_finish: date
	id_responsible: int

def updates_version_doc(data: DataForUpdateDoc) -> None:
	"""Обновляет версию документа."""
	with SQLite() as cursor:
		cursor.execute("PRAGMA foreign_keys = ON")
		cursor.execute("""
			UPDATE documents
			SET
				version = version + 1,
				date_start = :date_start,
				date_finish = :date_finish,
				id_responsible = :id_responsible
			WHERE id = :id_doc
		""", data)
		return


class DataForChangeDoc(TypedDict):
	id_doc: int
	actual: Literal[0, 1]

def change_actual_doc(data: DataForChangeDoc) -> None:
	"""Изменяет актуальность документа."""
	with SQLite() as cursor:
		cursor.execute("PRAGMA foreign_keys = ON")
		cursor.execute("""
			UPDATE documents
			SET
				actual = :actual
			WHERE id = :id_doc
		""", data)
		return
