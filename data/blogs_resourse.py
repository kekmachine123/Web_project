from data import db_session
from flask_restful import abort, Resource, reqparse
from flask import abort, jsonify
from data.news import News
import os


parser = reqparse.RequestParser()
parser.add_argument('title', required=True, type=str)
parser.add_argument('text', required=True, type=str)
parser.add_argument('user_id', required=True, type=int)

secret_api_key = 1337


def abort_if_blogs_not_found(blog_id):
    db_sess = db_session.create_session()
    blogs = db_sess.query(News).get(blog_id)
    db_sess.close()
    if not blogs:
        abort(404, f'Blog {blog_id} not found')


class BlogsResource(Resource):
    def get(self, blog_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_blogs_not_found(blog_id)
        db_sess = db_session.create_session()
        blogs = db_sess.query(News).get(blog_id)
        db_sess.close()
        return jsonify(
            {
                'blogs': [blogs.to_dict(only=('title', 'text', 'user_id', 'image', 'likes', 'dislikes'))]
            }
        )

    def delete(self, blog_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_blogs_not_found(blog_id)
        db_sess = db_session.create_session()
        blogs = db_sess.query(News).get(blog_id)
        if blogs.image != 'default_blog_img.jpg' and blogs.image:
            os.remove(os.path.join('static\\uploads\\', blogs.image))
        db_sess.delete(blogs)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    def put(self, blog_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_blogs_not_found(blog_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        blogs = db_sess.query(News).get(blog_id)
        blogs.title = args['title']
        blogs.text = args['text']
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class BlogsListResource(Resource):
    def get(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        db_sess = db_session.create_session()
        all_blogs = db_sess.query(News).all()
        if not all_blogs:
            return {'error': 'No blogs published'}
        db_sess.close()
        return {'blogs': [blog.to_dict(only=('title', 'text', 'image', 'likes', 'dislikes', 'user_id'))
                          for blog in all_blogs]}

    def post(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        args = parser.parse_args()
        db_sess = db_session.create_session()
        blog = News(
            text=args['text'],
            title=args['title'],
            user_id=args['user_id']
        )
        blog.image = 'default_blog_img.jpg'
        db_sess.add(blog)
        db_sess.commit()
        db_sess.close()



