from http import HTTPStatus
from http.client import HTTPException
from flask.blueprints import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate

from database.UserCollection import UserCollection
from model.UserModel import UpdateUserModel
from util import Collections
from util.bsion_utils import bson_to_json

user_blueprint = Blueprint('user', __name__)
from database import databaseInstance, timestamp_helper_projection


@user_blueprint.get('/who_ami')
@jwt_required()
def default_user():
    email = get_jwt_identity()
    user_collection = databaseInstance.db.get_collection(Collections.USER)
    user= user_collection.find_one({'email': email}, {**timestamp_helper_projection,'password': 0})
    if user:
        return bson_to_json(user), 200
    raise HTTPException({'message':'same things went wrong'}, HTTPStatus.INTERNAL_SERVER_ERROR)

@user_blueprint.get('/goback')
def goback():
    return {
        "response": "goback"
    }

@user_blueprint.put('/')
@validate()
@jwt_required()
def update_user(body: UpdateUserModel):
    email = get_jwt_identity()
    user_collection = databaseInstance.db.get_collection(Collections.USER)
    user= user_collection.find_one_and_update({'email': email}, { '$set': { UserCollection.FULL_NAME: body.full_name, UserCollection.PHONE_NUMBER: body.phone_number}})
    if user:
        new_user = user_collection.find_one({UserCollection.EMAIL: email})
        return bson_to_json(new_user), 200
    raise HTTPException({'message':'same things went wrong sorry!'}, HTTPStatus.INTERNAL_SERVER_ERROR)
