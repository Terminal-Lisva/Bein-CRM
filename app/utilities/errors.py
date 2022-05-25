from enum import Enum


class Errors(Enum):

	VALIDATION = {
		"errors": {
			1: "Некорректный токен приглашения",
			2: "Некорректный/несложный пароль",
			3: "Некорректный email",
		},
		"status_code": 404
	}

	NO_DATA = {
		"errors": {
			1: "Токен приглашения не найден",
			2: "ФИО не найдена",
			3: "Email/пароль не найден",
			4: "Данные ресурса не найдены",
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
			1: "Текущий пароль неверный",
		},
		"status_code": 403
	}

	NO_PERMISSION = {
		"errors": {
			1: "Нет разрешения на просмотр этого ресурса",
		},
		"status_code": 403
	}

	REQUEST_METHOD = {
		"errors": {
			1: "HTTP-метод не найден",
		},
		"status_code": 405
	}

	REQUEST_DATA = {
		"errors": {
			1: "Не удалось прочитать данные из запроса",
		},
		"status_code": 400
	}

	REQUEST_AUTH = {
		"errors": {
			1: "Сессия не установлена",
		},
		"status_code": 401
	}

#Пример ошибки:
#{
#	"source": "Пароль: qwerty123",
#	"type": "VALIDATION",
#	"message": "Некорректный/несложный пароль"
#}

#{
#	"source": "Session",
#	"type": "NO_PERMISSION",
#	"message": "Нет разрешения на просмотр этого ресурса"
#}
