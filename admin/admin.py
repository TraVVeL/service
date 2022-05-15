import sqlite3
from flask import Blueprint, session, g, render_template, request, flash, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import math
import time
import re
from FDataBase import FDataBase

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

UPLOAD_FOLDER = 'static/images/productImg'
ALLOWED_EXTENSIONS = {'jpeg', 'png', 'ico', 'jpg', 'svg', 'psd', 'webp'}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
dbase = None
db = None


def login_admin():
    session["admin_logged"] = 1


def is_logged():
    return True if session.get("admin_logged") else False


def logout_admin():
    session.pop("admin_logged")


menu = [{"url": ".index", "title": "Panel"},
        {"url": ".user_order", "title": "List orders"},
        {"url": ".user_issues", "title": "User issue"},
        {"url": ".products", "title": "List product"},
        {"url": ".user_list", "title": "List user"},
        {"url": ".add_product", "title": "Add product"},
        {"url": ".logout", "title": "Logout"}]


@admin.before_request
def before_request():
    """establish connection to the DB before executing the request"""
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request


@admin.route("/")
def index():
    if not is_logged():
        return redirect((url_for(".login")))

    return render_template("admin/index.html", menu=menu, title="Admin panel")


@admin.route("/login", methods=["POST", "GET"])
def login():
    if is_logged():
        return redirect(url_for(".index"))

    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["password"] == "admin":
            login_admin()
            return redirect(url_for(".index"))
        else:
            flash("Неверны логин или пароль", "error")

    return render_template("admin/login.html", title="Admin panel")


@admin.route("/logout", methods=["POST", "GET"])
def logout():
    if not is_logged():
        return redirect(url_for(".login"))

    logout_admin()

    return redirect(url_for(".login"))


@admin.route("/products", methods=["GET", "POST"])
def products():
    if not is_logged():
        return redirect(url_for(".login"))

    if request.form.getlist("checkbox_value"):
        selected_checkbox = (tuple(i for i in request.form.getlist("checkbox_value")))
        query = "FROM products WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox)))
        if db:
            try:
                cur = db.cursor()
                d = cur.execute("SELECT imgname " + query, selected_checkbox)
                s = cur.fetchall()
                if d is not None and len(selected_checkbox) > 0:
                    for i in s:
                        os.remove(str(UPLOAD_FOLDER + '/' + i[0]))
                    cur.execute("DELETE " + query, selected_checkbox)
                    db.commit()
            except sqlite3.Error as e:
                print("Error script getting data from DB'\n'error comes from admin.py | products " + str(e))

    product = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT id, "
                        f"name, "
                        f"description, "
                        f"quick_describe, "
                        f"weight, "
                        f"amount, "
                        f"price, "
                        f"url, "
                        f"imgname FROM products ORDER BY time DESC")
            product = cur.fetchall()
        except sqlite3.Error as e:
            print("Error script getting data from DB'\n'error comes from admin.py | products " + str(e))

    return render_template("admin/list_product.html",
                           title="КОЛЛЕКЦИЯ",
                           menu=menu,
                           product=product)


@admin.route("/user-list", methods=["POST", "GET"])
def user_list():
    if not is_logged():
        return redirect(url_for('.login'))

    if request.form.getlist("checkbox_value_user"):
        selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_user")))
        query = "DELETE FROM users WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
        if db:
            try:
                cur = db.cursor()
                cur.execute(query, selected_checkbox_user)
                db.commit()
            except sqlite3.Error as e:
                print("Error script getting data from DB'\n'error comes from admin.py | user_list " + str(e))

    list_user = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT id, name, email FROM users")
            list_user = cur.fetchall()
        except sqlite3.Error as e:
            print("Error script getting data from DB'\n'error comes from admin.py | user_list  " + str(e))

    return render_template("admin/list_user.html",
                           title="A list of users",
                           menu=menu,
                           list_user=list_user)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@admin.route("/add_product", methods=["POST", "GET"])
def add_product():
    error_helper = ''
    dbase = FDataBase(db)
    tm = math.floor(time.time())
    if request.method == "POST":

        if 'file' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)

        if request.form['weight'].isdigit() is False:
            res = ''
            error_helper += '  Вес может быть только целочисленным числом'
        if request.form['price'].isdigit() is False:
            res = ''
            error_helper += '  Цена может быть только целочисленным числом'

        match = re.compile('[A-Za-z0-9_.-~-]')
        gen = [i for i in request.form['url']]
        d = match.findall(request.form['url'])

        if (set(d) == set(gen) and '/' not in gen and '\\' not in gen) is False:
            res = ''
            error_helper += '  Не характерные символы для url'

        if error_helper == '' and file and allowed_file(file.filename):
            # file will renamed into time + his own name
            file.filename = request.form['name'] + str(tm) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            res = dbase.add_product(request.form['name'],
                                    request.form['description'],
                                    request.form['quick_describe'],
                                    request.form['weight'],
                                    request.form['amount'],
                                    request.form['price'],
                                    request.form['url'],
                                    filename)

            if not res:
                flash(error_helper.lstrip().replace('  ', '<br>'), category='error')

            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash(error_helper.lstrip().replace('  ', '<br>'), category='error')

    return render_template('admin/add_product.html', title="Product addition", menu=menu)


@admin.route("/user_issues", methods=["POST", "GET"])
def user_issues():
    if not is_logged():
        return redirect(url_for('.login'))

    if request.form.getlist("checkbox_value_issues"):

        if request.form["change_data"] == 'Mark as read':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_issues")))
            query = "UPDATE contact SET viewed='viewed-true' " \
                    "WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_list " + str(e))

        if request.form["change_data"] == 'Mark as unread':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_issues")))
            query = "UPDATE contact SET viewed='viewed-false' WHERE id IN ({})".format(
                ", ".join("?" * len(selected_checkbox_user)))
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_list " + str(e))

        if request.form["change_data"] == 'Delete selected':
            print('Delete Selected')
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_issues")))
            query = "DELETE FROM contact WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            print(query, selected_checkbox_user)
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_list " + str(e))

    get_information = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT * FROM contact ORDER BY time DESC")
            get_information = cur.fetchall()
            print(get_information, 'hi')
        except sqlite3.Error as e:
            print("Error script getting data from DB'\n'error comes from admin.py | user_list  " + str(e))

    return render_template("admin/user_issues.html",
                           title="A list of issues",
                           menu=menu,
                           get_information=get_information)


@admin.route("/user_order", methods=["POST", "GET"])
def user_order():
    if not is_logged():
        return redirect(url_for('.login'))

    if request.form.getlist("checkbox_value_order"):

        if request.form["change_data"] == 'Mark as delivered':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_order")))
            query = "UPDATE user_information SET delivered='delivered' " \
                    "WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_order " + str(e))

        if request.form["change_data"] == 'Mark as processing':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_order")))
            query = "UPDATE user_information SET delivered='processing' " \
                    "WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_order " + str(e))

        if request.form["change_data"] == 'Mark as canceled':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_order")))
            query = "UPDATE user_information SET delivered='canceled' " \
                    "WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_order " + str(e))
        if request.form["change_data"] == 'Delete selected':
            selected_checkbox_user = (tuple(i for i in request.form.getlist("checkbox_value_order")))
            query = "DELETE FROM user_information WHERE id IN ({})".format(", ".join("?" * len(selected_checkbox_user)))
            print(query, selected_checkbox_user)
            if db:
                try:
                    cur = db.cursor()
                    cur.execute(query, selected_checkbox_user)
                    db.commit()
                except sqlite3.Error as e:
                    print("Error script getting data from DB'\n'error comes from admin.py | user_list " + str(e))

    get_order = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT * FROM user_information")
            get_order = cur.fetchall()
        except sqlite3.Error as e:
            print("Error script getting data from DB'\n'error comes from admin.py | user_list  " + str(e))

    return render_template("admin/list_order.html",
                           title="A list of orders",
                           menu=menu,
                           get_order=get_order)
