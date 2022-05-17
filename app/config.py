import logging
from abc import abstractmethod
from utilities.other import Email


#---------------------------------ФИЛЬТР-------------------------------------
class Filter(logging.Filter):
    """Фильтр"""

    __func_name: str

    def __init__(self, func_name):
        self.__func_name = func_name
    
    def filter(self, record: logging.LogRecord) -> bool:
        return record.funcName == self.__func_name


#--------------------------------ОБРАБОТЧИКИ---------------------------------
class Handler(logging.Handler):
    """Обработчик"""

    def __init__(self):
        logging.Handler.__init__(self)
    
    @abstractmethod
    def emit(self, record: logging.LogRecord) -> None:
        raise NotImplementedError()


class HandlerRecordingFile(Handler):
    """Обработчик записи в файл"""

    __file_name: str

    def __init__(self, filename):
        super().__init__()
        self.__file_name = filename

    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)
        with open(self.__file_name, 'a') as f:
            f.write(text + "\n")


class HandlerSendByEmail(Handler):
    """Обрабочтик отправки на эл. почту"""

    __email: Email
    __to: str
    __subject: str

    def __init__(self, to, subject):
        super().__init__()
        self.__email = Email()
        self.__to = to
        self.__subject = subject
    
    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)
        self.__email.send(self.__to, self.__subject, text)
    

#-------------------------------КОНФИГУРАЦИЯ---------------------------------
logger_config = {
    'version' : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'universal_formatter': {
            'format': '{asctime} - {message}',
            'style': '{'
        }
    },
    'filters': {
        'user_registration': {
            '()': Filter,
            'func_name': 'records_log_user_registration'
        },
        'user_restorer': {
            '()': Filter,
            'func_name': 'records_log_user_restorer'
        },
        'user_authentication': {
            '()': Filter,
            'func_name': 'records_log_user_authentication'
        },
    },
    'handlers': {
        'user_registration': {
            '()': HandlerRecordingFile,
            'level': 'INFO',
            'filename': './app/logs/user_registration.txt',
            'formatter': 'universal_formatter',
            'filters': ['user_registration']
        },
        'user_restorer': {
            '()': HandlerRecordingFile,
            'level': 'INFO',
            'filename': './app/logs/user_restorer.txt',
            'formatter': 'universal_formatter',
            'filters': ['user_restorer']
        },
        'user_authentication': {
            '()': HandlerRecordingFile,
            'level': 'INFO',
            'filename': './app/logs/user_authentication.txt',
            'formatter': 'universal_formatter',
            'filters': ['user_authentication']
        },
        'error_500': {
            '()': HandlerSendByEmail,
            'level': 'ERROR',
            'to': '***@*****.**',
            'subject': 'Error info portal',
            'formatter': 'universal_formatter'
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': [
                'user_registration', 
                'user_restorer', 
                'user_authentication',
                'error_500'
            ] 
        }
    }
}