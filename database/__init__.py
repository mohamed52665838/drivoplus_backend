from flask_pymongo import PyMongo
databaseInstance = PyMongo()


def user_indexes():
    users_collection = databaseInstance.db.get_collection('user')
    users_collection.create_index("email", unique=True)
    users_collection.create_index("username", unique=True)

timestamp_helper_projection = {
   'created_at': 0,
    'updated_at':0
}

# user_indexes()
