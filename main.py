from flask import Flask, render_template, redirect
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vladik'


db_session.global_init('db/website.db')


if __name__ == '__main__':
    app.run()

