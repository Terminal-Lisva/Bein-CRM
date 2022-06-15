from flask import Flask
import logging.config
from config import logger_config
from database.db import DATABASE_NAME


app = Flask(__name__)


#SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///./database/{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Logging
logging.config.dictConfig(logger_config)
app.logger = logging.getLogger('app_logger')


#Load Routes
from views import *
