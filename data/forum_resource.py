from data import db_session
from flask_restful import abort, Resource, reqparse
from flask import abort, jsonify
from data.threads import Threads
import os


secret_api_key = 1337


parser = reqparse.RequestParser()
parser.add_argument('text', required=True, type=str)
parser.add_argument('user_id', required=True, type=int)


def abort_if_not_forum(thread_id):
    db_sess = db_session.create_session()
    blogs = db_sess.query(Threads).get(thread_id)
    db_sess.close()
    if not blogs:
        abort(404, f'Blog {thread_id} not found')


class ForumResource(Resource):
    def get(self, thread_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_not_forum(thread_id)
        db_sess = db_session.create_session()
        thread = db_sess.query(Threads).get(thread_id)
        thrs = [str(i.id) for i in db_sess.query(Threads).filter(Threads.ancestor_thread_id == thread.id).all()]
        db_sess.close()
        return jsonify(thread.to_dicte(thrs))

    def delete(self, thread_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_not_forum(thread_id)
        db_sess = db_session.create_session()
        thread = db_sess.query(Threads).get(thread_id)
        if thread.image:
            os.remove(os.path.join('static\\uploads\\', thread.image))
        for t in db_sess.query(Threads).filter(Threads.ancestor_thread_id == thread.id).all():
            if t.image:
                os.remove(os.path.join('static\\uploads\\', t.image))
            db_sess.delete(t)
        db_sess.delete(thread)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    def put(self, thread_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_not_forum(thread_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        thread = db_sess.query(Threads).get(thread_id)
        thread.text = args['text']
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class ForumListResource(Resource):
    def get(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        db_sess = db_session.create_session()
        threads = db_sess.query(Threads).filter(Threads.ancestor_thread_id == -10).all()
        if not threads:
            return jsonify({'error': {'Nothing published'}})
        db_sess.close()
        return {'threads': [i.to_dict(only=("theme", 'user_id', 'text' , 'created_date', 'image')) for i in threads]}

    def post(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        db_sess = db_session.create_session()
        args = parser.parse_args()
        thread = Threads(
            text=args['text'],
            user_id=args['user_id']
        )
        thread.theme = 'Другое'
        db_sess.add(thread)
        db_sess.commit()
        db_sess.close()
