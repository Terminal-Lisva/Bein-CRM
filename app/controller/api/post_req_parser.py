from controller.api import for_api
import re


class ErrorGettingID(Exception):
    """Ошибка получения id"""

    def __init__(self, source):
        self.source = f'Не удалось прочитать: {source}'


def get_id(path: str, href: str) -> int:
    """Получает id."""
    template_href = for_api.make_href(path)
    pattern = re.compile(f"^({template_href})(/)(?P<id>\d+)$")
    match = pattern.match(href)
    if match is None:
        raise ErrorGettingID(source=href)
    return int(match.groupdict()['id'])
