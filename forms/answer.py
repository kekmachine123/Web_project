from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, BooleanField


class AnswerForm(FlaskForm):
    text = TextAreaField('Содержание')
    is_anonym = BooleanField("Оставить анонимно")
    submit = SubmitField("Опубликовать")