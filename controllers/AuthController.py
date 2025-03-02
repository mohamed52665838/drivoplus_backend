import datetime
import logging
import random

from flask.blueprints import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from werkzeug.exceptions import HTTPException

from config import scheduler
from model.MessageModel import Message
from model.TokenActivateModel import TokenActivateModel, TokenActivateModelFields
from model.TokenModel import TokenModel
from services.mailer_service import send_mail
from util import Collections
from util import  hash_password, check_password
from database.UserCollection import UserCollection
from services.jwt_service import app_create_access_token, app_create_refresh_token
from model.UserModel import UserSignUpDto, SignInDto
from database import databaseInstance, timestamp_helper_projection
from util.bsion_utils import bson_to_json


auth_blueprint = Blueprint('auth', __name__)
class UnAuthorizedRequest(HTTPException):
    def __init__(self, message = 'username or password incorrect', code=401):
        self.code = code
        super().__init__(message)


@auth_blueprint.post("/signup")
@validate(on_success_status=201)
def signup_user(body: UserSignUpDto):
    user_collection = databaseInstance.db.get_collection(Collections.USER)
    body.timestamp_snapshot()
    body.password = hash_password(body.password).decode()
    res = user_collection.insert_one(body.model_dump())
    assert res.inserted_id is not None
    user = user_collection.find_one({UserCollection.USERNAME: body.username})
    random_otp_code = str(random.randint(100000, 999999))

    send_mail(
       subject=f"Your Code : {random_otp_code}",
        body="Test Body",
        recipients=[body.email]
    )

    otp_model = {
       'email': body.email,
       'code': random_otp_code
    }

    inserted_row = databaseInstance.db.get_collection(Collections.OTP_VALIDATOR).insert_one(otp_model)
    assert inserted_row.inserted_id is not None
    # 30 minute to expire
    scheduler.add_job(id=str(inserted_row.inserted_id),func=lambda : expired_otp(body.email), run_date=datetime.datetime.now() + datetime.timedelta(minutes=30))
    token = app_create_access_token(body.email)
    refresh_token = app_create_refresh_token(body.email)
    logging.getLogger().info("USER SIGNED IN")
    return {
        'access_token': token,
        'refresh_token' : refresh_token
    }





@auth_blueprint.post("/signin")
@validate()
def signin(body: SignInDto):
  
    user = databaseInstance.db.get_collection(Collections.USER).find_one({'email': body.email}, timestamp_helper_projection)
    print(user)
    if user is None:
        raise UnAuthorizedRequest()

    password = user.pop('password')
    if not check_password(password, body.password):
        raise UnAuthorizedRequest()

    access_token = app_create_access_token(identity=body.email)
    refresh_token = app_create_refresh_token(identity=body.email)
    token = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    user_token = {
        'user' : bson_to_json(user),
        'tokens': token
    }
    return user_token, 200


@auth_blueprint.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = app_create_access_token(identity)
    refresh_token = app_create_refresh_token(identity)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }



@auth_blueprint.post("/confirm")
@validate()
def confirmation(body: TokenActivateModel):
    user = databaseInstance.db.get_collection(Collections.USER).find_one_and_update(
        {UserCollection.EMAIL: body.email},
        { '$set': {UserCollection.ACTIVATE_AT: datetime.datetime.now()}}
    )
    if user is None:
        return Message(
            message='Session expired, try login again please'
        )

    validator = databaseInstance.db.get_collection(Collections.OTP_VALIDATOR).find_one({TokenActivateModelFields.email: body.email})

    if validator is None or validator[TokenActivateModelFields.code] != body.code:
        return Message(
            message='Session expired, try login again please or incorrect error'
        )
    token = app_create_access_token(user['email'])
    refresh_token = app_create_access_token(user['email'])

    expired_otp(body.email)
    logging.info('User Confirm his Account')
    return {
        'user': user,
        'tokens': {
            'access_token': token,
            'refresh_token': refresh_token
        }
    }




# helper for this controller



# otp message send message
def expired_otp(email: str):
    databaseInstance.db.get_collection(Collections.OTP_VALIDATOR).delete_one({'email': email})
    user = databaseInstance.db.get_collection(Collections.USER).find_one({'email': email})
    if user and user.get(UserCollection.ACTIVATE_AT) is not None:
        return
    value = databaseInstance.db.get_collection(Collections.USER).delete_one({'email': email})
    assert value.deleted_count == 1



@auth_blueprint.get("/send-otp")
def send_otp():
    scheduler.add_job(
        id='expiration',
        func= lambda : print('schedule app just ran'),
        run_date = datetime.datetime.now() + datetime.timedelta(seconds=20)
    )
    # send_mail(
    #    subject="Otp",
    #     body="Test Body",
    #     recipients=['essid101010@gmail.com']
    # )
    return 'Mail Sent Successfully'