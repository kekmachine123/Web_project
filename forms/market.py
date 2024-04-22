from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectField, BooleanField, StringField, IntegerField
from wtforms.validators import DataRequired


class Market(FlaskForm):
    choices = ['Электроника', 'Мебель', 'Одежда', 'Машины', 'Другое']

    category = SelectField("Категория", choices=choices, validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    cost = IntegerField("Цена", validators=[DataRequired()])
    address = StringField('Адрес продавца', validators=[DataRequired()])
    contact = StringField('Контакт продавца (email, номер телефона)', validators=[DataRequired()])
    submit = SubmitField('Создать')


class Filter(FlaskForm):
    cat_choose = SelectField("Категория товаров", choices=['Все', 'Электроника', 'Мебель', 'Одежда', 'Машины', 'Другое'],
                               validators=[DataRequired()])
    submit = SubmitField("Применить")