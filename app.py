import os
import models
import jwt
from flask import Flask, request
from flask_cors import CORS
from auth_middleware import token_required


app = Flask(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'

app.config['SECRET_KEY'] = SECRET_KEY
app.config['CORS_ORIGINS'] = 'http://localhost:4200'
CORS(app, resources='/*')


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        user_model = models.get_or_create_user(data['username'])
        token = jwt.encode({"user_id": str(user_model["_id"])}, app.config["SECRET_KEY"], algorithm="HS256")
        return {
            "message": "Successfully fetched auth token",
            "error": None,
            "data": {
                'id': str(user_model['_id']),
                'username': user_model['username'],
                'token': token
            }
        }
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


@app.route('/topics', methods=["GET"])
def get_all_topics():
    return models.get_all_topics(), 200


@app.route('/questions', methods=["GET"])
def get_questions_by_topic():
    args = request.args
    return models.get_questions_by_topic(args.get('topic_id')), 200


@app.route('/vote', methods=["POST"])
@token_required
def vote(user):
    data = request.json
    question_id = data.get('question_id')
    up_down = data.get('up_down')
    models.vote_question(user, question_id, up_down)
    return {"ok": True}, 200


@app.route('/add-question', methods=["POST"])
@token_required
def add_question(user):
    data = request.json
    question = data.get('question')
    topic_id = data.get('topic_id')
    created_question = models.add_question(question, topic_id, user)
    return created_question, 201

# @app.route("/post-questions", methods=["POST"])
# def tmp_post_questions():
#     data = request.json
#     models.tmp_publish_questions(data)
#     return {"ok": True}, 201


if __name__ == '__main__':
    app.run()
