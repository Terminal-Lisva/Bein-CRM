from app import app
from flask_restful import Api
from utilities import const
from resources.session import Session, SessionNew
from resources.users import Users, UsersPassword
from resources.pages import App, Account


api = Api(app)

api.add_resource(Session, f'/{const.prefix_api}/session')
api.add_resource(SessionNew, f'/{const.prefix_api}/session/new')
api.add_resource(Users, f'/{const.prefix_api}/users')
api.add_resource(UsersPassword, f'/{const.prefix_api}/users/password')

api.add_resource(App, '/app')
api.add_resource(Account, '/app/account')
