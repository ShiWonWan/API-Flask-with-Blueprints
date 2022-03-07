# imports
from flask import Blueprint, jsonify, request, abort
from flask_pymongo import ObjectId, MongoClient
from jwt import encode
from datetime import datetime, timedelta # for the user registration time
import hashlib # to make a hash of the user's password (strongly recommended)

# PyMongo config
# I recommend using environment variables, but for this example I'm not going to use them.
connection_str = 'mongodb://localhost/' # replace with the mongo uri server
client = MongoClient(connection_str)
#    database_name.collection
#             ⇩       ⇩
db = client.blogApp.user

# Hashing
def hash_str(str):
    return hashlib.sha256(str.encode()).hexdigest()

# BLUEPRINT CONFIGS
#           blueprint name                       path
#                  ⇩                              ⇩
user = Blueprint('user', __name__, url_prefix='/user')

# If user exist
def existing_user(user):
    return True if db.find_one({'user' : user}) else False

# Create a new user
@user.route('/new', methods=['POST'])
def new_user():

    # Catching the values
    user = request.json['user']
    password = hash_str(request.json['password'])
    name = request.json['name']

    # User comprobations
    if user == None or password == None or name == None or user == '' or request.json['password'] == '' or name == '':
        abort(400) # Missing values
    if existing_user(user):
        abort(404) # User exist
    
    # User registration
    id = db.insert_one({
        'user' : user,
        'password' : password,
        'date' : datetime.today(),
        'name' : name
    })

    return jsonify({'_id' : str(ObjectId(id.inserted_id))})

# Login
@user.route('/login', methods=['POST'])
def login():

    # Catching the values
    user = request.json['user']
    password = hash_str(request.json['password'])

    # User comprobations
    if user == None == password == None or user == '' or request.json['password'] == '':
        abort(400) # Missing values
    if not existing_user(user):
        abort(404) # User not exist

    user_values = db.find_one({'user' : user})
    if user_values['password'] != password:
        return jsonify({'login' : False})
    else:
        access_token = encode({
            'user' : user_values['user'], 
            'name' : user_values['name'],
            '_id' : str(ObjectId(user_values['_id'])),
        }, 'secret passwor', algorithm='HS256')
    
    return jsonify({'login' : True, 'token' : access_token})

# Update user
@user.route('/update/<id>', methods=['PUT'])
def update_user(id):

    # Catching the values
    user = request.json['user']
    password = hash_str(request.json['password'])
    name = request.json['name']

    # User comprobations
    if user == None == password == None or user == '' or request.json['password'] == '' or name == None or name == '':
        abort(400) # Missing values
    if not existing_user(user):
        abort(404) # User not exist

    # Make the update
    if db.find_one({'_id':ObjectId(id)}):
        db.update_one({'_id':ObjectId(id)},
        {'$set': {
            'user': user,
            'password': password,
            'name': name,
            'date': datetime.today()
        }})
    else:
        abort(404) # user not found
    return jsonify({'_id' : str(ObjectId(id))})

# Delte user
@user.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    
    # Find and delete the user
    if db.find_one({'_id':ObjectId(id)}):
        db.delete_one({'_id':ObjectId(id)})
    else:
        abort(404)
    return jsonify({'deleted' : True})