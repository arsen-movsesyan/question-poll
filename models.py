from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


client = MongoClient('localhost', 27017)
db = client['question-poll']


def id_to_string(obj):
    if '_id' in obj:
        obj['_id'] = str(obj['_id'])
    return obj


def create_user(username):
    user_collection = db.users
    user_id = user_collection.insert_one({"username": username}).inserted_id
    return {
        "_id": user_id,
        "username": username
    }


def get_user(username):
    user_collection = db.users
    user = user_collection.find_one({"username": username})
    return user


def get_user_by_id(user_id):
    user_collection = db.users
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    return user


def get_or_create_user(username):
    user = get_user(username)
    if user is None:
        user = create_user(username)
    return user


def get_questions_by_topic(topic_id=None):
    collection = db.questions
    query = {"topic_id": int(topic_id)}
    if topic_id is None:
        query = {}
    return [id_to_string(q) for q in collection.find(query)]


def get_all_topics():
    collection = db.topics
    topics = collection.find({}, {"_id": False})
    return list(topics)


def vote_question(user, question_id, up_down):
    collection = db.questions
    question = collection.find_one({'_id': ObjectId(question_id)})
    username = user.get('username')
    if up_down:
        if username in question['voted_up']:
            collection.update_one({'_id': ObjectId(question_id)}, {'$pull': {'voted_up': username}})
        elif username in question['voted_down']:
            collection.update_one({'_id': ObjectId(question_id)}, {'$pull': {'voted_down': username}})
            collection.update_one({'_id': ObjectId(question_id)}, {'$push': {'voted_up': username}})
        else:
            collection.update_one({'_id': ObjectId(question_id)}, {'$push': {'voted_up': username}})
    else:
        if username in question['voted_down']:
            collection.update_one({'_id': ObjectId(question_id)}, {'$pull': {'voted_down': username}})
        elif username in question['voted_up']:
            collection.update_one({'_id': ObjectId(question_id)}, {'$pull': {'voted_up': username}})
            collection.update_one({'_id': ObjectId(question_id)}, {'$push': {'voted_down': username}})
        else:
            collection.update_one({'_id': ObjectId(question_id)}, {'$push': {'voted_down': username}})
    return collection.find_one({'_id': ObjectId(question_id)})


def add_question(question, topic_id, user):
    collection = db.questions
    now = datetime.now()
    obj = {
        "question": question,
        "topic_id": topic_id,
        "voted_up": [],
        "voted_down": [],
        "submitted_by": user.get('username'),
        "submitted_at": now.strftime("%Y-%m-%d %H:%M:%S")
    }
    question_id = collection.insert_one(obj).inserted_id
    created_question = collection.find_one({"_id": question_id}, {"_id": False})
    return created_question

# def tmp_publish_questions(topics):
#     for t in topics:
#         print(t)
#         topic_collection = db.topics
#         topic_collection.insert_one(t)
