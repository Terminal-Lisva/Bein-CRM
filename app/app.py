from flask import Flask
import logging.config
from config import logger_config


app = Flask(__name__)


#SQLAlchemy
DATABASE_NAME = './database/info_portal.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_NAME}'


#Logging
logging.config.dictConfig(logger_config)
app.logger = logging.getLogger('app_logger')


#Load Routes
from views import *
