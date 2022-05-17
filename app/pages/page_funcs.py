from typing import List, Optional, Dict, Union, Any
from flask import request, typing as flaskTyping, jsonify, make_response, redirect, render_template
from utilities.enums import Errors


#Вспомогательные функции для страниц (функционал Flask):
def get_request_data(keys: List[str]) -> Optional[Dict[str, str]]:
    """Получает данные запроса."""
    request_data = request.get_json(force=True, silent=True)
    try:
        return {key: str(request_data[key]) for key in keys}
    except (TypeError, KeyError):
        return None

def get_cookie(name: str) -> Optional[str]:
    """Получает соответствующую куку."""
    return request.cookies.get(name)

def success_response(value: Union[list, bool]) -> flaskTyping.ResponseReturnValue:
    """Успешный ответ."""
    response = {
		"success": {
			"value": value,
		}
	}
    return jsonify(response)

def error_response(code_error: int, type_error: str) -> flaskTyping.ResponseReturnValue:
    """Ответ ошибка."""
    errors = eval(f'Errors.{type_error}')
    response = {
		"error": {
			"name": errors.value[code_error],
			"code": code_error
		}
	}
    return jsonify(response)

def make_success_response(value: Union[list, bool]) -> flaskTyping.ResponseReturnValue:
    """Сделанный успешный ответ."""
    return make_response(success_response(value))

def redirect_response(route: str) -> flaskTyping.ResponseReturnValue:
    """Перенаправляемый ответ."""
    return make_response(redirect(route))

def template_response(template: str, data: Any = None) -> flaskTyping.ResponseReturnValue:
    """Шаблонный ответ."""
    return make_response(render_template(template, data=data))

def add_cookies_to_response(response: flaskTyping.ResponseReturnValue, cookie_session: str, cookie_auth: str) -> None:
    """Добавляет куки сессии и авторизации к ответу."""
    response.set_cookie(key='Session', value=cookie_session, httponly=True)
    response.set_cookie(key='Auth', value=cookie_auth, max_age=60*60*24*30, httponly=True)

def add_cookie_session_to_response(response: flaskTyping.ResponseReturnValue, cookie_session: Optional[str]) -> None:
    """Добавляет куки сессии к ответу."""
    if cookie_session is None: return
    response.set_cookie(key='Session', value=cookie_session, httponly=True)

def delete_cookies(response: flaskTyping.ResponseReturnValue) -> None:
    """Удаляет куки."""
    response.delete_cookie('Session')
    response.delete_cookie('Auth')

def get_current_page_uri() -> str:
    """Получает текущий URI страницы."""
    return request.path