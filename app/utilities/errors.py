from enum import Enum


class Errors(Enum):

	VALIDATION = {
		"errors": {
			1: "Некорректный токен приглашения",
			2: "Некорректный или несложный пароль",
			3: "Некорректный email",
		},
		"status_code": 404
	}

	NO_DATA = {
		"errors": {
			1: "Токен приглашения не найден",
			2: "Пользователь не найден",
		},
		"status_code": 404
	}

	ALREADY_DATA = {
		"errors": {
			1: "Пользователь уже зарегистрирован",
			2: "Пользователь еще не зарегистрирован",
		},
		"status_code": 404
	}

	FALSE_DATA = {
		"errors": {
			1: "Неверный пароль",
		},
		"status_code": 403
	}

	NO_PERMISSION = {
		"errors": {
			1: "Нет разрешения на просмотр или редактирование этого ресурса",
		},
		"status_code": 403
	}

	NO_AUTHENTICATION = {
		"errors": {
			1: "Сессия не установлена",
		},
		"status_code": 401
	}

	BAD_REQUEST = {
		"errors": {
			1: "Неопознанный путь",
		},
		"status_code": 404
	}


#Пример ошибки:
#{
#	"source": "Пароль: qwerty123",
#	"type": "VALIDATION",
#	"message": "Некорректный или несложный пароль"
#}
