from flask import Flask, render_template, redirect, session, make_response, request, flash, url_for
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from forms.loginform import LoginForm
import os
from forms.blog import BlogCreationForm
from data.news import News
from forms.forum import CreateThreadForm, ThemeChoose
from data.threads import Threads
from forms.answer import AnswerForm
from PIL import Image
from news_parser import NewsFromInternet
from forms.market import Market, Filter
from data.sells import Sells
from flask_restful import reqparse, abort, Api, Resource
from data import blogs_resourse, sells_resource, forum_resource, news_resourse


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'vladik'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JSON_AS_ASCII'] = False
UPLOAD_FOLDER = 'static\\uploads\\'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
nws = NewsFromInternet()
today_news = nws.get_vl_ru_news()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


def image_size_scale(filename):
    try:
        im = Image.open("static/uploads/" + filename)
        (width, height) = im.size
        d = (width ** 2 + height ** 2) ** 0.5
        h = str(int(height * (500 / d)))
        w = str(int(width * (500 / d)))
        return (w, h)
    except Exception:
        return 250, 300


app.jinja_env.globals.update(image_size_scale=image_size_scale)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def f(answer_to):
    q = db_sess.query(Threads).filter(Threads.id == answer_to).first()
    if q.user_id == 0:
        return q.text, "Аноним", q.id
    return q.text, q.user.name, q.id


app.jinja_env.globals.update(f=f)


def answers_counter(id):
    answs = list([str(i.id) for i in db_sess.query(Threads).filter(Threads.answer_to == id).all()])
    return ">>" + '>>'.join(answs), len(answs)


app.jinja_env.globals.update(answers_counter=answers_counter)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/create_blog", methods=['GET', 'POST'])
@login_required
def create_news():
    form = BlogCreationForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        blog = News(
            title=form.title.data,
            text=form.text.data,
            image=filename,
            user_id=db_sess.query(User).filter(User.name == current_user.name).first().id
        )
        db_sess.add(blog)
        db_sess.commit()
        return redirect("/blogs")
    return render_template('create_blog.html', title='Создание записи', form=form)


@app.route("/")
def home():
    return render_template("base.html", title="Главная")


@app.route("/blogs", methods=['GET', 'POST'])
def blogs():
    news = db_sess.query(News).all()
    return render_template("blogs.html", news=news)


@app.route("/blogs/<blog_id>", methods=['GET', 'POST'])
def blog_page(blog_id, message=''):
    content = db_sess.query(News).filter(News.id == blog_id).first()
    return render_template("blog_page.html", content=content, message=message)


@app.route("/forum", methods=['GET', 'POST'])
def forum():
    theme_choose = ThemeChoose()
    if theme_choose.validate_on_submit():
        choice = theme_choose.theme_choose.data
        if theme_choose.theme_choose.data != 'Все':
            data = db_sess.query(Threads).filter(Threads.ancestor_thread_id == -10).all()
            data = list(filter(lambda x: x.theme == choice, data))
        else:
            data = db_sess.query(Threads).filter(Threads.ancestor_thread_id == -10).all()
        return render_template("forum.html", data=data, theme_choose=theme_choose)
    data = db_sess.query(Threads).filter(Threads.ancestor_thread_id == -10).all()
    return render_template("forum.html", data=data, theme_choose=theme_choose)


@app.route("/forum/<branch_id>", methods=["GET", "POST"])
def branch_page(branch_id):
    main = db_sess.query(Threads).filter(Threads.id == branch_id).first()
    data = db_sess.query(Threads).filter(Threads.ancestor_thread_id == branch_id).all()
    return render_template("branch_page.html", data=data, main=main)


@app.route("/answer_to/<branch_id>/<thread_id>", methods=["GET", "POST"])
@login_required
def answer(branch_id, thread_id):
    form = AnswerForm()
    filename = 0
    if form.validate_on_submit():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        thread = Threads(
            text=form.text.data,
            ancestor_thread_id=branch_id,
        )
        if thread_id != '0':
            thread.answer_to = thread_id
        else:
            thread.answer_to = branch_id
        if filename:
            thread.image = filename
        if form.is_anonym.data:
            thread.user_id = 0
        else:
            thread.user_id = current_user.id
        db_sess.add(thread)
        db_sess.commit()
        return redirect(f"/forum/{branch_id}")
    return render_template("answer.html", form=form)


@app.route("/create_forum_branch", methods=['GET', 'POST'])
@login_required
def create_forum_branch():
    form = CreateThreadForm()
    filename = 0
    if form.validate_on_submit():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        thread = Threads(
            theme=form.theme.data,
            text=form.text.data
        )
        if filename:
            thread.image = filename
        if form.is_anonym.data:
            thread.user_id = 0
        else:
            thread.user_id = current_user.id
        db_sess.add(thread)
        db_sess.commit()
        return redirect("/forum")
    return render_template("create_thread.html", form=form, title='Создать ветку форума')


@app.route("/like/<blog_id>", methods=['GET', 'POST'])
@login_required
def like(blog_id):
    blog = db_sess.query(News).filter(News.id == blog_id).first()
    if str(current_user.id) in blog.who_liked:
        return render_template("blog_page.html", content=blog, message='Вы уже поставили лайк')
    blog.who_liked = ";".join([blog.who_liked, str(current_user.id)])
    blog.likes += 1
    if str(current_user.id) in blog.who_disliked:
        meow = blog.who_disliked.split(";")
        meow.remove(str(current_user.id))
        blog.who_disliked = ';'.join(meow)
        blog.dislikes -= 1
        db_sess.commit()
        return render_template("blog_page.html", content=blog, message='Дизлайк сменен на лайк')
    db_sess.commit()
    return render_template("blog_page.html", content=blog, message='Лайк поставлен')


@app.route("/dislike/<blog_id>", methods=['GET', 'POST'])
@login_required
def dislike(blog_id):
    blog = db_sess.query(News).filter(News.id == blog_id).first()
    if str(current_user.id) in blog.who_disliked:
        return render_template("blog_page.html", content=blog, message='Вы уже поставили дизлайк')
    blog.who_disliked = ";".join([blog.who_disliked, str(current_user.id)])
    blog.dislikes += 1
    if str(current_user.id) in blog.who_liked:
        meow = blog.who_liked.split(";")
        meow.remove(str(current_user.id))
        blog.who_liked = ';'.join(meow)
        blog.likes -= 1
        db_sess.commit()
        return render_template("blog_page.html", content=blog, message='Лайк сменен на дислайк')
    db_sess.commit()
    return render_template("blog_page.html", content=blog, message='Дизайк поставлен')


@app.route("/userprofile/<user_id>", methods=['GET', 'POST'])
def userprofile(user_id):
    user = db_sess.query(User).filter(User.id == user_id).first()
    last_blogs = list(user.news)[-3:]
    last_threads = list(user.threads)[-3:]
    return render_template("userprofile.html", user=user, last_blogs=last_blogs, last_threads=last_threads)


@app.route("/news")
def news():
    return render_template("news.html", data=today_news)


@app.route("/news/<news_id>")
def news_page(news_id):
    item = list(filter(lambda x: x['id'] == news_id, today_news))[0]
    return render_template("news_page.html", item=item)


@app.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():
    form = Market()
    if form.validate_on_submit():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        s = Sells(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            image=filename,
            address=form.address.data,
            contact=form.contact.data,
            category=form.category.data,
            money=form.cost.data
        )
        db_sess.add(s)
        db_sess.commit()
        return redirect("/market")
    return render_template("sell.html", form=form)


@app.route("/market", methods=['GET', 'POST'])
def market():
    form = Filter()
    data = db_sess.query(Sells).all()
    if form.validate_on_submit():
        choice = form.cat_choose.data
        if choice != 'Все':
            data = list(filter(lambda x: x.category == choice, data))
        return render_template("market.html", data=data, form=form)
    return render_template("market.html", data=data, form=form)


@app.route("/market/<sell_id>", methods=['GET', 'POST'])
def sell_page(sell_id):
    item = db_sess.query(Sells).filter(Sells.id == sell_id).first()
    return render_template("sell_page.html", item=item)


@app.route("/delete_from_market/<sell_id>", methods=['GET', 'POST'])
def delete_from_market(sell_id):
    item = db_sess.query(Sells).filter(Sells.id == sell_id).first()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image))
    db_sess.delete(item)
    db_sess.commit()
    return redirect("/market")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == '__main__':
    db_session.global_init('db/website.db')
    db_sess = db_session.create_session()
    api.add_resource(blogs_resourse.BlogsResource, '/api/blogs/<int:blog_id>/<int:secret_key>')
    api.add_resource(blogs_resourse.BlogsListResource, '/api/blogs/<int:secret_key>')
    api.add_resource(sells_resource.SellsResource, '/api/market/<int:sell_id>/<int:secret_key>')
    api.add_resource(sells_resource.SellsListResource, '/api/market/<int:secret_key>')
    api.add_resource(forum_resource.ForumResource, '/api/forum/<int:thread_id>/<int:secret_key>')
    api.add_resource(forum_resource.ForumListResource, '/api/forum/<int:secret_key>')
    api.add_resource(news_resourse.NewsResource, '/api/news')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


