from typing import List, Optional, Dict, Union
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

def success_response_with_cookies(value: Union[list, bool], cookie_session: str, cookie_auth: str) -> flaskTyping.ResponseReturnValue: 
    """Успешный ответ с куками. Применяется для авторизации по лог и паролю."""
    response = make_response(success_response(value))
    response.set_cookie(key='Session', value=cookie_session, httponly=True)
    response.set_cookie(key='Auth', value=cookie_auth, max_age=60*60*24*30, httponly=True)
    return response

def redirect_response(route: str, cookie_session: Optional[str] = None) -> flaskTyping.ResponseReturnValue:
    """Перенаправляемый ответ. Может быть с кукой сессии."""
    response = make_response(redirect(route))
    if cookie_session is not None:
        response.set_cookie(key='Session', value=cookie_session, httponly=True)
    return response

def render_template_response(template_name: str, cookie_session: Optional[str] = None) -> flaskTyping.ResponseReturnValue:
    """Ответ с передачей шаблона."""
    response = make_response(render_template(template_name))
    if cookie_session is not None:
        response.set_cookie(key='Session', value=cookie_session, httponly=True)
    return response

def delete_cookies() -> flaskTyping.ResponseReturnValue:
    """Удаляет куки."""
    response = make_response(success_response(value=True))
    response.delete_cookie('Session')
    response.delete_cookie('Auth')
    return response