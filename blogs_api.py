# import flask
# from flask import jsonify
# from data import db_session
# from data.news import News
#
#
# blueprint = flask.Blueprint(
#     'blogs_api',
#     __name__,
#     template_folder='templates'
# )
#
#
# @blueprint.route('/api/blogs')
# def get_blogs():
#     db_sess = db_session.create_session()
#     blogs = db_sess.query(News).all()
#     return jsonify(
#         {
#             'blogs': [item.to_dict(only=('title', 'text', 'user.name')) for item in blogs]
#         }
#     )
