from typing import Any
from flask import (request, typing as flaskTyping, jsonify, make_response,
render_template)


#Вспомогательные функции API Flask:
def get_data_from_request_in_json() -> dict:
    """Получает данные из запроса в формате JSON."""
    data = request.get_json(silent=True)
    return data if data is not None else {}

def make_json_response(
    document: dict,
    status_code: int) -> flaskTyping.ResponseReturnValue:
    """Делает ответ в формате JSON."""
    return make_response(jsonify(document), status_code)

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
