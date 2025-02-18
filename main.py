import json
import logging
from http import HTTPStatus
from controllers.PaymentController import payment_blueprint
from services import configJWT
from controllers.AuthController import auth_blueprint
from flask import Flask
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.exceptions import HTTPException
from config import CONFIG, mailer, scheduler, log_formatter
from controllers.UserController import user_blueprint
from database import databaseInstance, user_indexes

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
app.config["MAIL_SERVER"] = CONFIG['MAILER_SERVER']
app.config["MAIL_PORT"] = int(CONFIG['MAILER_PORT'])
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = CONFIG['MAILER_USERNAME']
app.config["MAIL_PASSWORD"] = CONFIG['MAILER_PASSWORD']
app.config["MAIL_DEFAULT_SENDER"] = CONFIG['MAILER_USERNAME']

databaseInstance.init_app(app=app,uri=CONFIG['DATABASE_URL'] )
configJWT.init_app(app)
mailer.init_app(app)
scheduler.init_app(app)
scheduler.start()



with app.app_context():
    user_indexes()
    logging.info("APPLICATION STARTED TEST")

app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(auth_blueprint, url_prefix='/auth')


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    print('this function executed')
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(DuplicateKeyError)
def handle_exception(e: DuplicateKeyError):
    """Return JSON instead of HTML for HTTP errors."""
    return {
        'label': f'database operation error code: {e.code} mongo standards',
        'message': e.details.get('errmsg'),
        'error': e.details.get("keyPattern"),

    }, HTTPStatus.CONFLICT


# Ajouter la route Stripe
app.register_blueprint(payment_blueprint, url_prefix='/payment')
