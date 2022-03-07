from flask import Blueprint, jsonify, request, abort
from datetime import datetime
from flask_pymongo import MongoClient, ObjectId


# PyMongo config
connection_str = 'mongodb://localhost/'
client = MongoClient(connection_str)
db = client.blogApp.blog

# BLUEPRINT CONFIGS
blog = Blueprint('blog', __name__, url_prefix='/blog')

# Create a new blog /blog/new
@blog.route('/new', methods=['POST'])
def newblog():
    id = db.insert_one({
        'name' : request.json['name'],
        'text' : request.json['text'],
        'date' : datetime.today()
    })

    return jsonify({'_id' : str(ObjectId(id.inserted_id))})

# Get all blogs /blog/get
@blog.route('/get')
def get_all():
    docs = []

    for doc in db.find():
        docs.append({
            'name' : doc['name'],
            'text' : doc['text'],
            'date' : doc['date'],
            '_id' : str(ObjectId(doc['_id']))
        })

    return jsonify(docs)

# Get one blog
@blog.route('/get/<id>')
def get_one(id):
    blog = db.find_one({'_id' : ObjectId(id)})
    if not blog:
        abort(404)
    else:
        del blog['_id']
        return jsonify(blog)

# Update blog
@blog.route('/update/<id>', methods=['PUT'])
def update_blog(id):

    # Catching the values
    name = request.json['name']
    text = request.json['text']
    date = datetime.today()

    # User comprobations
    if name == None or name == '' or text == None or text == '':
        abort(400) # Missing values
    # Make the update
    if db.find_one({'_id':ObjectId(id)}):
        db.update_one({'_id':ObjectId(id)},
        {'$set': {
            'name': name,
            'text': text,
            'date': date
        }})
    else:
        abort(404) # blog not found
    return jsonify({'_id' : str(ObjectId(id))})

# Delete one blog
@blog.route('/delete/<id>', methods=['DELETE'])
def delete_one(id):
    db.delete_one({'_id' : ObjectId(id)})
    reponse = jsonify({f'_id {id}' : 'deleted ok'})
    reponse.status_code = 200
    return reponse