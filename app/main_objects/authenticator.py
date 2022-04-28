from typing import *
from flask import request
from database.database import DatabaseUsers
from utilities.validations import ValidationEmail, ValidationPassword
from utilities.other import CookieSession, CookieAuthentication, HashingData


class Authenticator:
	"""Аутентификатор (pattern facade)"""
	
	def __init__(self):
		self.__db = DatabaseUsers()
	
	def authenticates_user(self, email: str = None, password: str = None) -> Dict[str, Union[Optional[int], Optional[str]]]:
		"""Аутентифицирует пользователя"""
		if email is None or password is None:
			return self.__authenticates_user_by_cookies()
		return self.__authenticates_user_by_email_and_password(email, password)
		
	def __authenticates_user_by_email_and_password(self, email: str, password: str) -> Dict[str, Union[Optional[int], Optional[str]]]:
		"""Аутентифицирует пользователя по емайлу и паролю"""
		if not ValidationEmail(email).get_result():
			return {
				"user_id": None,
				"cookie_session": None,
				"cookie_auth": None,
				"error_code": 5
			}
		elif not ValidationPassword(password).get_result():
			return {
				"user_id": None,
				"cookie_session": None,
				"cookie_auth": None,
				"error_code": 6
			}
		hashed_password = HashingData(password).calculate_hash()
		user_id = self.__db.get_user_id((email, hashed_password))
		if user_id is None:
			return {
				"user_id": None,
				"cookie_session": None,
				"cookie_auth": None,
				"error_code": 7
			}
		cookie_session = CookieSession().creates_cookie(user_id)
		cookie_auth = CookieAuthentication().creates_cookie(email, hashed_password)
		return {
			"user_id": user_id,
			"cookie_session": cookie_session,
			"cookie_auth": cookie_auth,
			"error_code": None
		}
	
	def __authenticates_user_by_cookies(self) -> Dict[str, Union[Optional[int], Optional[str]]]:
		"""Аутентифицирует пользователя по кукам"""
		request_cookies = request.cookies
		request_cookie_session = request_cookies.get('Session')
		request_cookie_auth = request_cookies.get('Auth')
		if request_cookie_session is not None:
			try:
				user_id, hashed_user_id = CookieSession().get_data_from_cookie(request_cookie_session)
				assert hashed_user_id == HashingData(user_id).calculate_hash()
				return {
					"user_id": user_id,
					"cookie_session": None,
					"cookie_auth": None,
					"error_code": None
				}
			except AssertionError: #для некорректной или подделанной куки
				pass
		elif request_cookie_auth is not None:
			try:
				email, hashed_password = CookieAuthentication().get_data_from_cookie(request_cookie_auth)
				user_id = self.__db.get_user_id((email, hashed_password))
				assert user_id is not None
				cookie_session = CookieSession().creates_cookie(user_id)
				return {
					"user_id": user_id,
					"cookie_session": cookie_session,
					"cookie_auth": None,
					"error_code": None
				}
			except AssertionError: #для некорректной или подделанной куки
				pass
		return {
			"user_id": None,
			"cookie_session": None,
			"cookie_auth": None,
			"error_code": None
		}