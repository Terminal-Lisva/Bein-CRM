import sqlite3


class SQLite:
	"""База данных - SQLite"""

	def __init__(self):
		self.__file = "./app/database/info_portal.sqlite"
		self.__connect = None

	def __enter__(self):
		self.__connect = sqlite3.connect(self.__file)
		return self.__connect.cursor()

	def __exit__(self, type, value, traceback):
		if self.__connect: self.__connect.commit(); self.__connect.close()
