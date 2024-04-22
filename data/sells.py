import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Sells(SqlAlchemyBase):
    __tablename__ = "sells"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    image = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    contact = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    category = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    money = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
