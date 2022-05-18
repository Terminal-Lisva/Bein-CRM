from .page import PageAvailableWithSideMenu
from flask import typing as flaskTyping


class AppPage(PageAvailableWithSideMenu):
    """Главная страница приложения"""

    def __init__(self):
        super().__init__(template='app_page.html')