from .page import PageAvailableWithSideMenu
from flask import typing as flaskTyping


class AccountPage(PageAvailableWithSideMenu):
    """Страница акаунта"""

    def __init__(self):
        super().__init__(template='account_page.html')
    
    