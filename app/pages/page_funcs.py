from typing import List, Optional, Dict,  Any, Union
from flask import (request, typing as flaskTyping, jsonify, make_response,
redirect, render_template)
from utilities.errors import Errors


#Вспомогательные функции для страниц (функционал Flask):
def get_data_from_json(keys: List[str]) -> Optional[Dict[str, str]]:
    """Получает данные запроса."""
    request_data = request.get_json(force=True, silent=True)
    try:
        return {key: str(request_data[key]) for key in keys}
    except (TypeError, KeyError):
        return None

def get_data_from_url(args: List[str]) -> Optional[Dict[str, str]]:
    """Получает данные из URL."""
    try:
        return {arg: str(request.args.get(arg)) for arg in args}
    except Exception: #надо тестировать на тип исключения
        return None

def get_cookie(name: str) -> Optional[str]:
    """Получает соответствующую куку."""
    return request.cookies.get(name)

def success_response(
    response: Dict[str, Any],
    status_code: int) -> flaskTyping.ResponseReturnValue:
    """Сообщение об успешном ответе."""
    return jsonify(response), status_code

def error_response(
    source_error: str,
    type_error: str,
    code_error: int) -> flaskTyping.ResponseReturnValue:
    """Подробное сообщение об ошибке с использованием универсального типа."""
    errors = eval(f'Errors.{type_error}')
    message = errors.value["errors"][code_error]
    status_code = errors.value["status_code"]
    response = {
        "source": source_error,
        "type": type_error,
        "message": message
    }
    return jsonify(response), status_code

def make_success_response(
    response: Dict[str, Any],
    status_code: int) -> flaskTyping.ResponseReturnValue:
    """Сделать успешный ответ."""
    return make_response(success_response(response, status_code))

def redirect_response(to: str) -> flaskTyping.ResponseReturnValue:
    """Перенаправление."""
    return redirect(to), 302


#def redirect_response
#    """Перенаправляемый ответ."""
#    return make_response()

def template_response(
    template: str,
    data: Any = None) -> flaskTyping.ResponseReturnValue:
    """Шаблонный ответ."""
    return make_response(render_template(template, data=data))

def add_cookies_to_response(
    response: flaskTyping.ResponseReturnValue,
    cookie_session: Optional[str] = None,
    cookie_auth: Optional[str] = None) -> None:
    """Добавляет куки сессии и авторизации к ответу."""
    if cookie_session is not None:
        response.set_cookie(
            key='Session', value=cookie_session, httponly=True)
    if cookie_auth is not None:
        response.set_cookie(
            key='Auth', value=cookie_auth, max_age=60*60*24*30, httponly=True)
    return

def delete_cookies(response: flaskTyping.ResponseReturnValue) -> None:
    """Удаляет куки."""
    response.delete_cookie('Session')
    response.delete_cookie('Auth')
    return

def get_current_page_uri() -> str:
    """Получает текущий URI страницы."""
    return request.path
