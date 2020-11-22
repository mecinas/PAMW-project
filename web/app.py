from flask import Flask, request, make_response, session, render_template, flash, url_for
from flask_session import Session
from redis import Redis
from os import getenv
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime

db = Redis(host='redis', port='6379', db=0)
load_dotenv()
SESSION_TYPE = 'filesystem'
SESSION_REDIS = db
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY=True
REMEMBER_COOKIE_HTTPONLY = True
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
app.debug = False
ses = Session(app)


def is_user(username):
    return db.hexists(f"user:{username}", "password")


@app.route('/')
def open_home():
    return render_template("home.html")


@app.route("/sender/register", methods=['GET'])
def open_register():
    return render_template("register.html")


def redirect(url, status=301):
    response = make_response('', status)
    response.headers['Location'] = url
    return response


def is_login(login):
    return db.hexists(f"user:{login}", "password")


def verify_user(login, password):
    password_encoded = password.encode()
    hashed_password_database = db.hget(f"user:{login}", "password")
    if not hashed_password_database:
        return False
    return checkpw(password_encoded, hashed_password_database)


def save_user(firstname, lastname, email, adress, login, password):
    salt = gensalt(5)
    password_encoded = password.encode()
    hashed_password = hashpw(password_encoded, salt)
    db.hset(f"user:{login}", "firstname", firstname)
    db.hset(f"user:{login}", "lastname", lastname)
    db.hset(f"user:{login}", "email", email)
    db.hset(f"user:{login}", "adress", adress)
    db.hset(f"user:{login}", "password", hashed_password)


def validate_input(firstname, lastname, email, adress, login, password, sec_password):
    if not firstname:
        flash("Nie wpisano imienia!")
    if not lastname:
        flash("Nie wpisano nazwiska!")
    if not email:
        flash("Nie wpisano email-a!")
    if not adress:
        flash("Nie wpisano adresu!")
    if not login:
        flash("Nie wpisano loginu!")
    if not password:
        flash("Nie wpisano hasła!")
    if sec_password != password:
        flash("Wpisane hasła nie zgadzają się!")
        return redirect(url_for('open_register'))
    if firstname and lastname and email and adress and login and password:
        if is_login(login):
            flash("Podany login już istnieje!")
            return redirect(url_for('open_register'))
        save_user(firstname, lastname, email, adress, login, password)
        flash("Poprawnie zarejestrowano!")
        return redirect(url_for('open_login'))

    return redirect(url_for('open_register'))


@app.route("/sender/register", methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    adress = request.form.get('adress')
    login = request.form.get('login')
    password = request.form.get('password')
    sec_password = request.form.get('sec_password')

    return validate_input(firstname, lastname, email, adress,
                          login, password, sec_password)


@app.route("/sender/login", methods=['GET'])
def open_login():
    return render_template("login.html")


@app.route("/sender/login", methods=['POST'])
def login():
    login = request.form.get("login")
    password = request.form.get("password")

    if not verify_user(login, password):
        flash("Podano nieprawidłowy login lub hasło")
        return render_template("login.html")
        
    flash("Zalogowano!")
    session[login] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return render_template("login.html")


@app.route("/sender/logout", methods=['GET'])
def open_logout():
    session.clear()
    flash("Wylogowano!")
    return render_template("login.html")

@app.route("/sender/dashboard")
def open_dashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    app.run()
