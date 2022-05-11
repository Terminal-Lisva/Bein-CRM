from flask import Flask
import logging.config
from config import logger_config


app = Flask(__name__)


#Logging
logging.config.dictConfig(logger_config)
app.logger = logging.getLogger('app_logger')


#Load Routes
from routes import *