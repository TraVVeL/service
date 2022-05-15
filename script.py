from flask import Flask, render_template, request, flash, redirect, url_for, g, jsonify, Blueprint, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from FDataBase import FDataBase
from UserLogin import UserLogin
from forms import LoginForm
from admin.admin import admin
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import time
import math

DATABASE = '/tmp/siteData.db'
UPLOAD_FOLDER = 'static/images/productImg'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'siteData.db')))
app.config['SECRET_KEY'] = 'kgf5tlbghb5906yymerffv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
login_manager = LoginManager(app)
dbase = None
DEBUG = True
app.register_blueprint(admin, url_prefix='/admin')


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


"""---------DATABASE CONNECTION ---------"""


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


"""---------DATABASE CLOSE---------"""


# Check if the user is logged in. If true, change the login form to profile
def check_authenticated(name):
    if current_user.is_authenticated:
        name = ['Профиль', 'Выйти', 'profile', 'logout']
        return name
    else:
        return ['Войти', '', 'login', 'login']


# all data use like request.form where default values is dash(-)
all_data = {'phone': '-', 'email': '-', 'message': '-', 'name': '-', 'surname': '-',
            'color': '-', 'price': '-', 'viewed': 'viewed-false'}

order_data = {'name': '-', 'phone': '-', 'mail': '-', 'secondary_name': '-', 'secondary_phone': '-', 'city': '-',
              'street': '-', 'building_address': '-', 'entrance': '-', 'floor': '-', 'apartment': '-', 'deliver': '-',
              'deliver_time': '-', 'note': '-', 'delivered': 'processing', 'user_id': '-'}

purchase_data = {'user_id': '-', 'product_name': '-', 'product_id': '-', 'product_count': '-',
                 'final_cost': '-', 'product_price': '-', 'product_url': '-', 'product_img': '-'}


# list using to put 1 of 3 variables to class \\ default class name is flash
subcategory = ['flash', 'flash success', 'flash error']


@app.route('/')
def index():
    return render_template('index.html',
                           products=dbase.get_products_announce(),
                           check_authenticated=check_authenticated)


@app.route('/state')
def state():
    db = get_db()
    dbase = FDataBase
    return render_template('state.html', menu=dbase.getMenu())


@app.route('/services')
def service():
    return render_template('services.html', check_authenticated=check_authenticated)


@app.route('/product')
def product():
    return render_template('product.html',
                           products=dbase.get_products_announce(),
                           check_authenticated=check_authenticated,
                           title="НАША КОЛЛЕКЦИЯ")


@app.route('/about')
def about():
    return render_template('about.html', check_authenticated=check_authenticated)


@app.route('/contact')
def contact():
    return render_template('contact.html', check_authenticated=check_authenticated)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm
    errors = ''

    if request.method == "POST":
        user = dbase.get_user_by_email(request.form['email'])

        if user and check_password_hash(user['password'], request.form['password']):
            user_login = UserLogin().create(user)
            rm = True if request.form.get('remindme') else False
            login_user(user_login, remember=rm)
            return redirect(url_for('profile'))

        if user is False and request.form['email'] != 'Логин':
            errors += 'Логин имеет неправильный характер'
        if user and check_password_hash(user['password'], request.form['password']) is False:
            errors += 'Пароль имеет неправильный характер'
        if request.form['email'] == 'Логин' or request.form['password'] == 'Пароль':
            errors = 'Вы указали пустое поле ввода  '

        flash(errors, category='error')

    return render_template("login.html", check_authenticated=check_authenticated, form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form["password"]) > 5 and request.form["password"] == request.form["password1"]:
            hash = generate_password_hash(request.form["password"])
            res = dbase.add_user(request.form["name"], request.form["email"], hash, 1000, 'пусто')
            if res:
                flash('Успешная регистрация', category='success')
                return redirect(url_for('login'))
            else:
                flash('error type', category='error')
        else:
            flash('password or name error', category='error')

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли с аккаунта', category='success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    user_id = current_user.get_id()
    print(user_id)

    user = [current_user.get_id(), current_user.get_name(), current_user.get_cash(), current_user.get_cart()]
    return render_template('profile.html',
                           user=user,
                           ordered=dbase.ordered(user_id),
                           user_info=dbase.user_info(user_id),
                           check_authenticated=check_authenticated)


@app.route("/product/<alias>", methods=["POST", "GET"])
def show_product(alias):
    id, name, description, quick_describe, weight, amount, price, imgname = dbase.get_product(alias)
    result_amount = ''
    for i in amount:
        if i != '.':
            result_amount += i
        if i == '.':
            result_amount += i + '<br>'

    result_amount = result_amount[:-4]

    if not name:
        abort(404)

    if request.method == 'POST':
        # Convert user data into a dictionary
        data_get_order = request.form.to_dict(flat=True)
        # Checking what data we get and if string is empty or id doesn't exists convert into dash symbol(-)
        print(data_get_order)
        for i in data_get_order.keys():
            if len(data_get_order[i]) > 0:
                order_data[i] = data_get_order[i]
        res = dbase.order(*tuple(i for i in order_data.values()))
        print(data_get_order, res, order_data)
        if res:
            flash('Данные отправлены', category='success')

        else:
            flash('Непредвиденные обстоятельста, пожалуйста повторите попытку', category='error')

    return render_template('post.html',
                           menu=dbase.get_menu(),
                           post=dbase.get_product(alias),
                           products=dbase.get_products_announce(),
                           result_amount=result_amount,
                           name=name,
                           )


@app.route("/agreement")
def agreement():
    return render_template("agreement.html")


# Checking the information to add to the database from @app.route index
# Processing the data we get
@app.route('/render_user_issue', methods=['POST'])
def render_user_issue():
    # Convert user data into a dictionary
    data_get = request.form.to_dict(flat=True)

    # showing user message if some went wrong or success
    message = ['Что-то пошло не так, отправтьте данные повторно', 'Данные отправлены']
    # Checking what data we get and if string is  empty or id doesn't exists convert into dash symbol(-)
    for i in data_get.keys():
        # if length of data is less than 1 all_data element will get dash symbol(-)
        if len(data_get[i]) > 0:
            all_data[i] = data_get[i]
    # trying to send user data\\ if res not response than res will return false
    res = dbase.add_information(*tuple(i for i in all_data.values()))
    if res:
        return jsonify({'category': subcategory[1], 'content': message[1]})

    return jsonify({'category': subcategory[2], 'content': message[0]})


@app.route('/user_purchase', methods=["POST", "GET"])
def user_purchase():
    message = ['Что-то пошло не так, повторите попытку', 'Заказ принят']
    data_get = request.form.to_dict(flat=True)
    if data_get:
        print(data_get)
        tm = math.floor(time.time())
        if len(data_get) == 8:
            for i in data_get.keys():
                # if length of data is less than 1 purchase_data element will get dash symbol(-)
                if len(data_get[i]) > 0:
                    purchase_data[i] = data_get[i]
            # trying to send user data\\ if res not response than res will return false
            res = dbase.product_purchase(*tuple(i for i in purchase_data.values()))

        if len(data_get) == 15:

            for i in data_get.keys():
                # if length of data is less than 1 order_data element will get dash symbol(-)
                if len(data_get[i]) > 0:
                    order_data[i] = data_get[i]

            # trying to send user data\\ if res not response than res will return false
            res_inf = dbase.user_information(*tuple(i for i in order_data.values()))
            if res_inf:
                return jsonify({'category': subcategory[1], 'content': message[1]})

    return jsonify({'category': subcategory[2], 'content': message[0]})


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html",
                           products=dbase.get_products_announce(),
                           check_authenticated=check_authenticated)


if __name__ == '__main__':
    app.run(debug=True)
