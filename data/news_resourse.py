from data import db_session
from flask_restful import abort, Resource, reqparse
from flask import abort, jsonify
from data.news import News
from main import today_news


class NewsResource(Resource):
    def get(self):
        return jsonify({'today_news': today_news})
