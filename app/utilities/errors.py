from enum import Enum


class Errors(Enum):

	VALIDATION = {
		"errors": {
			1: "Некорректный токен приглашения",
			2: "Некорректный/несложный пароль",
			3: "Некорректный/несложный новый пароль",
			4: "Некорректное ФИО",
			5: "Некорректный Email",
		},
		"status_code": 403
	}

	NO_DATA = {
		"errors": {
			1: "Токен приглашения не найден",
			2: "ФИО не найдена",
			3: "Пользователь еще не зарегистрирован",
			4: "Email/пароль не найден",
		},
		"status_code": 403
	}

	ALREADY_DATA = {
		"errors": {
			1: "Пользователь уже зарегистрирован",
		},
		"status_code": 403
	}

	FALSE_DATA = {
		"errors": {
			1: "Текущий пароль неверный",
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
			1: "Пользователь не аутентифицирован",
		},
		"status_code": 401
	}
