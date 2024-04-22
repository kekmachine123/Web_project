from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired


class CreateThreadForm(FlaskForm):
    choices = ['Еда', 'Политика', 'Шоппинг', 'Образование', 'Наука',
               'История', 'Спорт', 'Развлечения', 'Природа', 'Другое']

    theme = SelectField("Тема", choices=choices, validators=[DataRequired()])
    text = TextAreaField('Содержание', validators=[DataRequired()])
    is_anonym = BooleanField("Оставить анонимно")
    submit = SubmitField("Опубликовать")


class ThemeChoose(FlaskForm):
    theme_choose = SelectField("Тема", choices=['Все', 'Еда', 'Политика', 'Шоппинг', 'Образование', 'Наука',
                                                      'История', 'Спорт', 'Развлечения', 'Природа', 'Другое'],
                               validators=[DataRequired()])
    submit = SubmitField("Применить")
