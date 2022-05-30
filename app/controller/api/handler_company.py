


class HandlerRequestGetCompany(HandlerRequestWithAuthentication):
    """Обработчик запроса на получение компаний"""

    def __init__(self):
        super().__init__()

    def handle(self) -> Optional[Tuple[Dict[str, Any], int]]:
        """Обрабатывает запрос на получение компаний."""
