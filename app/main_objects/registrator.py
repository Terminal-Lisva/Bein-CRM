from typing import *
from database.database import DatabaseUsers
from utilities.validations import ValidationInvitationToken, ValidationPassword, ValidationFIO
from utilities.other import HashingData


class Registrator:
	"""Регистратор (pattern facade)"""
	def __init__(self):
		self.__db = DatabaseUsers()

	def forms_data_for_user_registration(self, invitation_token: str) -> Dict[str, Optional[tuple]]:
		"""Формирует данные для регистрации пользователя"""
		if not ValidationInvitationToken(invitation_token).get_result():
			return {"data": None, "error_code": 1}
		user_data_from_db = self.__db.get_user_data(invitation_token)
		if user_data_from_db is None:
			return {"data": None, "error_code": 2}
		return {"data": user_data_from_db, "error_code": None}
	
	def registers_user(self, invitation_token: str, password: str) -> Dict[str, Optional[tuple]]:
		"""Регистрирует пользователя"""
		if not ValidationInvitationToken(invitation_token).get_result():
			return {"error_code": 1}
		elif not ValidationPassword(password).get_result():
			return {"error_code": 3}
		user_id = self.__db.get_user_id(invitation_token)
		if user_id is None:
			return {"error_code": 2}
		try:
			self.__adds_user_to_database(user_id, password)
		except AssertionError:
			return {"error_code": 4}
		return {"error_code": None}
	
	def restores_password(self, invitation_token: str, user_name: str, password: str) -> Dict[str, Optional[tuple]]:
		"""Восстанавливает пользователя"""
		if not ValidationInvitationToken(invitation_token).get_result():
			return {"error_code": 1}
		elif not ValidationFIO(user_name).get_result():
			return {"error_code": 8}
		elif not ValidationPassword(password).get_result():
			return {"error_code": 3}
		user_id = self.__db.get_user_id(invitation_token)
		if user_id is None:
			return {"error_code": 2}
		user_fio = self.__db.get_user_fio(user_id)
		if user_name != user_fio:
			return {"error_code": 9}
		try:
			self.__restores_user_to_database(user_id, password)
		except AssertionError:
			return {"error_code": 10}
		return {"error_code": None}
		
	def __adds_user_to_database(self, user_id: int, password: str) -> None:
		"""Добавляет пользователя в базу данных"""
		assert self.__db.check_user_authentication(user_id)
		hashed_password = HashingData(password).calculate_hash()
		self.__db.add_user_authentication(user_id, hashed_password)
	
	def __restores_user_to_database(self, user_id: int, password: str) -> None:
		"""Восстанавливает пользователя в базе данных"""
		assert not self.__db.check_user_authentication(user_id)
		self.__db.remove_user_authentication(user_id)
		hashed_password = HashingData(password).calculate_hash()
		self.__db.add_user_authentication(user_id, hashed_password)