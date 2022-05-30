from typing import Any
from flask import (request, typing as flaskTyping, jsonify, make_response,
render_template)
from utilities.errors import Errors


#Вспомогательные функции API Flask:
def get_data_from_json(keys: list[str]) -> dict[str, Any] | None:
    """Получает данные запроса."""
    request_data = request.get_json(force=True, silent=True)
    try:
        return {key: str(request_data[key]) for key in keys}
    except (TypeError, KeyError):
        return None

def make_json_response(
    response: dict,
    status_code: int) -> flaskTyping.ResponseReturnValue:
    """Делает ответ в формате JSON."""
    return make_response(jsonify(response), status_code)

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
    return make_json_response(response, status_code)

def template_response(
    template: str,
    data: Any = None) -> flaskTyping.ResponseReturnValue:
    """Шаблонный ответ."""
    return make_response(render_template(template, data=data), 200)

def add_cookies_to_response(
    response: flaskTyping.ResponseReturnValue,
    cookie_session: str | None = None,
    cookie_auth: str | None = None) -> None:
    """Добавляет куки сессии и авторизации к ответу."""
    if cookie_session is not None:
        response.set_cookie(
            key='Session', value=cookie_session, httponly=True)
    elif cookie_auth is not None:
        response.set_cookie(
            key='Auth', value=cookie_auth, max_age=60*60*24*30, httponly=True)
    return

def get_cookie(name: str) -> str | None:
    """Получает соответствующую куку."""
    return request.cookies.get(name)

def delete_cookies(response: flaskTyping.ResponseReturnValue) -> None:
    """Удаляет куки."""
    response.delete_cookie('Session')
    response.delete_cookie('Auth')
    return
