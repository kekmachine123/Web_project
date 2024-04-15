import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Threads(SqlAlchemyBase):
    __tablename__ = "threads"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    title = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)

    answer_to = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=-10)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
