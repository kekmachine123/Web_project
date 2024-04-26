from data import db_session
from flask_restful import abort, Resource, reqparse
from flask import abort, jsonify
from data.sells import Sells
import os


secret_api_key = 1337


parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('description', required=True, type=str)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('address', required=True, type=str)
parser.add_argument('contact', required=True, type=str)
parser.add_argument('money', required=True, type=int)


def abort_if_sells_not_found(sell_id):
    db_sess = db_session.create_session()
    sells = db_sess.query(Sells).get(sell_id)
    db_sess.close()
    if not sells:
        abort(404, f'Sell {sell_id} not found')


class SellsResource(Resource):
    def get(self, sell_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_sells_not_found(sell_id)
        db_sess = db_session.create_session()
        sells = db_sess.query(Sells).get(sell_id)
        db_sess.close()
        return jsonify(
            {
                'sells': [sells.to_dict(only=('name', 'description', 'created_date', 'user_id', 'address',
                                              'category', 'money', 'contact'))]
            }
        )

    def delete(self, sell_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_sells_not_found(sell_id)
        db_sess = db_session.create_session()
        sells = db_sess.query(Sells).get(sell_id)
        if sells.image != 'sells_default_img.jpg' and sells.image:
            os.remove(os.path.join('static\\uploads\\', sells.image))
        db_sess.delete(sells)
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})

    def put(self, sell_id, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        abort_if_sells_not_found(sell_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        sells = db_sess.query(Sells).get(sell_id)
        sells.name = args['name']
        sells.description = args['description']
        sells.address = args['address']
        sells.contact = args['contact']
        sells.money = args['money']
        db_sess.commit()
        db_sess.close()
        return jsonify({'success': 'OK'})


class SellsListResource(Resource):
    def get(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        db_sess = db_session.create_session()
        all_sells = db_sess.query(Sells).all()
        if not all_sells:
            return {'error': 'No sells published'}
        db_sess.close()
        return {'sells': [sell.to_dict(only=('name', 'description', 'created_date', 'user_id', 'address',
                                              'category', 'money', 'contact'))
                          for sell in all_sells]}

    def post(self, secret_key):
        if secret_key != secret_api_key:
            return jsonify({'error': 'unauthorized'})
        args = parser.parse_args()
        db_sess = db_session.create_session()
        sell = Sells(
            name=args['name'],
            description=args['description'],
            user_id=args['user_id'],
            address = args['address'],
            money = args['money'],
            contact = args['contact']
        )
        sell.image = 'sells_default_img.jpg'
        sell.category = 'Другое'
        db_sess.add(sell)
        db_sess.commit()
        db_sess.close()


