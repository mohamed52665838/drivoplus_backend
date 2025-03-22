import logging
from enum import StrEnum
import dotenv
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from logging.handlers import RotatingFileHandler


CONFIG = dotenv.dotenv_values('.env')

# Setup RotatingFileHandler
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')#format
rotating_handler = RotatingFileHandler('./tmp/app.log', maxBytes=1000000, backupCount=3)#taille du fichier 1 mo
rotating_handler.setFormatter(log_formatter)
rotating_handler.setLevel(logging.INFO)# tfasa5li les log lowlanin circulaire 

logging.getLogger().addHandler(rotating_handler)

logging.getLogger().setLevel(logging.INFO)
app_bcrypt = Bcrypt()
mailer = Mail()
scheduler = APScheduler()#5demt bih bich kain mail sartloch verification ba3ed 30 min ytfasa5 
