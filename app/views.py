from app import app
from flask_restful import Api
from resources.session import Session, SessionNew
from resources.users import Users, UsersPassword
from resources.pages import AppPage, AccountPage


api = Api(app)
prefix = "/api/1.0"

api.add_resource(Session, f'{prefix}/session')
api.add_resource(SessionNew, f'{prefix}/session/new')
api.add_resource(Users, f'{prefix}/users')
api.add_resource(UsersPassword, f'{prefix}/users/password')


api.add_resource(AppPage, '/app')
api.add_resource(AccountPage, '/app/account')
