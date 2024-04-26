import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Threads(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "threads"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    theme = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relationship('User')
    text = sqlalchemy.Column(sqlalchemy.String,
                             nullable=True)

    answer_to = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    ancestor_thread_id = sqlalchemy.Column(sqlalchemy.Integer, default=-10)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def to_dicte(self, thrs):
        if self.ancestor_thread_id == -10 and not self.answer_to:
            type = "Branch"
        else:
            type = "Answer"
        if type == "Branch":
            return {
                'id': self.id,
                'type': type,
                'theme': self.theme,
                'answers': ';'.join(thrs),
                'user_id': self.user_id,
                'created_date': self.created_date,
                'image': self.image
            }
        elif type == "Answer":
            return {
                'id': self.id,
                'type': type,
                'ancestor_thread_id': self.ancestor_thread_id,
                'answer_to': self.answer_to,
                'answers': ';'.join(thrs),
                'user_id': self.user_id,
                'created_date': self.created_date,
                'image': self.image
            }







