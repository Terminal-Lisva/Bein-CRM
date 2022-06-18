from enum import Enum


class Errors(Enum):
	NOT_VALID_TOKEN = "Некорректный токен приглашения", 404
	NOT_VALID_PASSWORD = "Некорректный или несложный пароль", 404
	NOT_VALID_EMAIL = "Некорректный email", 404
	NO_TOKEN = "Токен приглашения не найден", 404
	NO_USER = "Пользователь не найден", 404
	USER_IS_BD = "Пользователь уже зарегистрирован", 404
	USER_IS_NOT_BD = "Пользователь еще не зарегистрирован", 404
	FALSE_PASSWORD = "Неверный пароль", 403
	NO_PERMISSION_RESOURCE = "Нет разрешения на просмотр или редактирование этого ресурса", 403
	NO_AUTHENTICATION = "Сессия не установлена", 401
	NOT_FOUND_PATH = "Неопознанный путь", 400
	FILTER_ERROR = "Ошибка фильтрации", 400
	BAD_REQUEST = "Некорректный запрос", 400

#Пример ошибки:
#{
#	"source": "Пароль: qwerty123",
#	"type": "VALIDATION",
#	"message": "Некорректный или несложный пароль"
#}
