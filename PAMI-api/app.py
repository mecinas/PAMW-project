from flask import Flask, request, make_response, render_template, flash, url_for, g
from redis import StrictRedis
from os import getenv
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime
from jwt import encode, decode
import time
import jwt
from uuid import uuid4
import json

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PASS = getenv("REDIS_PASS")
db = StrictRedis(REDIS_HOST, db=15, password=REDIS_PASS, decode_responses=True)

SESSION_REDIS = db
SESSION_TYPE = 'filesystem'

SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
JWT_SECRET = getenv("JWT_SECRET")

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = JWT_SECRET
app.debug = False


def allowed_methods(methods, origin):
    if 'OPTIONS' not in methods:
        methods.append('OPTIONS')
    response = make_response('', 204)

    allowed_origins = ["http://localhost:3000",
                       "localhost", "http://localhost"]
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin

    response.headers['Access-Control-Allow-Methods'] = ', '.join(methods)
    response.headers["Access-Control-Allow-Headers"] = 'Content-Type, auth_cookie'
    response.headers["Access-Control-Allow-Credentials"] = 'true'
    return response


@app.route('/root', methods=['GET', 'OPTIONS'])
def root():
    if request.method == 'OPTIONS':
        return allowed_methods(['GET'])

    links = []
    links.append({"type": 'register', "url": '/sender/register'})
    links.append({"type": 'login', "url": '/sender/login'})
    links.append({"type": 'dashboard', "url": '/sender/dashboard'})

    document = {
        "data": {},
        "links": links
    }
    return document


@app.route("/root/sender/register", methods=['GET', 'OPTIONS'])
def open_register():
    if request.method == 'OPTIONS':
        return allowed_methods(['GET', 'POST'])

    links = []
    links.append({"type": 'root:parent', "url": '/'})
    document = {
        "data": {},
        "links": links
    }
    return document


@app.route("/root/sender/login", methods=['GET', 'OPTIONS'])
def open_login():
    if request.method == 'OPTIONS':
        return allowed_methods(['GET', 'POST'])

    links = []
    links.append({"type": 'root:parent', "url": '/'})
    document = {
        "data": {},
        "links": links
    }
    return document


@app.route("/root/sender/notifications", methods=['GET', 'OPTIONS'])
def open_notifications():
    if request.method == "OPTIONS":
        return allowed_methods(['GET'])
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    data = {
        "is_authorized": False,
    }
    document = {
        "data": data,
        "links": links
    }
    is_authorized(data)
    login = g.authorization.get("login")

    return document


@app.route("/root/sender/notifications/update", methods=['GET', 'OPTIONS'])
def update_notifications():
    if request.method == "OPTIONS":
        return allowed_methods(['GET'])
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    data = {
        "is_authorized": False,
        "notification": None
    }
    document = {
        "data": data,
        "links": links
    }
    if not is_authorized(data):
        return document

    login = g.authorization.get("login")
    while(data["notification"] is None):
        data["notification"] = db.lpop(f"notifications:{login}")

    return document

def is_authorized(data, cookie_name=None):
    token = request.headers.get("cookie")
    print(token)
    try:
        print(decode(token, JWT_SECRET, algorithms=['HS256']))
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e:
        return False

    login = g.authorization.get("login")
    if not is_login(login):
        return False
    data["is_authorized"] = True
    return True


@app.route("/root/sender/dashboard", methods=['GET', 'OPTIONS'])
def open_dashboard():
    if request.method == "OPTIONS":
        return allowed_methods(['GET', 'POST', 'DELETE'])
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    data = {
        "is_authorized": False,
        "has_packages": False,
        "packages": None,
        "login": None
    }
    document = {
        "data": data,
        "links": links
    }
    if not is_authorized(data):
        return document

    login = g.authorization.get("login")
    data["login"] = login
    packages = db.hget(f"user:{login}", "packages")
    if packages is None:
        return document

    data["has_packages"] = True
    data["packages"] = json.loads(packages)
    return document


def convert_to_output_packages(all_packages, packages_for_response):
    for (f_key, f_value) in all_packages.items():
        if f_value is not None:
            for (s_key, s_value) in json.loads(f_value).items():
                single_package = {
                    "sender_name": f_key[5:],
                    "id": s_key,
                    "adressee_name": s_value["adressee_name"],
                    "storeroom_id": s_value["storeroom_id"],
                    "size": s_value["size"],
                    "state": s_value["state"]
                }
                packages_for_response.append(single_package)


@app.route("/root/carrier/dashboard", methods=['GET', 'OPTIONS'])
def open_carrier_dashboard():
    origin = request.headers.get('Origin')
    if request.method == "OPTIONS":
        return allowed_methods(['GET', 'PUT'], origin)

    links = []
    links.append({"type": 'root:parent', "url": '/'})
    all_packages = {}
    packages_for_response = []
    data = {
        "all_packages": packages_for_response,
        "is_authorized": False
    }
    document = {
        "data": data,
        "links": links
    }
    token = request.headers.get("auth_cookie")
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e:
        return document
    data["is_authorized"] = True

    for key in db.scan_iter(): 
        if key[:5] == "user:":
            all_packages[key] = db.hget(f"{key}", "packages")

    convert_to_output_packages(all_packages, packages_for_response)

    allowed_origins = ["http://localhost:3000",
                       "localhost", "http://localhost"]
    response = make_response(document, 200)
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = 'true'
    return response


def is_login(login):
    return db.exists(f"user:{login}")


def verify_user(login, password):
    password_encoded = password.encode('utf-8')
    hashed_password_database = db.hget(
        f"user:{login}", "password").encode('utf-8')
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
    messages = []
    valid_input = False
    data = {
        "valid_input": valid_input,
        "messages": messages
    }
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    document = {
        "data": data,
        "links": links
    }
    if not firstname:
        messages.append("Nie wpisano imienia!")
    if not lastname:
        messages.append("Nie wpisano nazwiska!")
    if not email:
        messages.append("Nie wpisano email-a!")
    if not adress:
        messages.append("Nie wpisano adresu!")
    if not login:
        messages.append("Nie wpisano loginu!")
    if not password:
        messages.append("Nie wpisano hasła!")
    if sec_password != password:
        messages.append("Wpisane hasła nie zgadzają się!")
        return document
    if firstname and lastname and email and adress and login and password:
        if is_login(login):
            messages.append("Podany login już istnieje!")
            return document

        save_user(firstname, lastname, email, adress, login, password)
        messages.append("Poprawnie zarejestrowano!")
        valid_input = True
        data["valid_input"] = valid_input
        return document

    return document


@app.route("/root/sender/register", methods=['POST'])
def register():
    data = request.json
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    adress = data.get('adress')
    login = data.get('login')
    password = data.get('password')
    sec_password = data.get('sec_password')

    return validate_input(firstname, lastname, email, adress,
                          login, password, sec_password)


@app.route("/root/sender/login", methods=['POST'])
def login():
    data = request.json
    login = data.get('login')
    password = data.get('password')

    messages = []
    is_valid = True
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    data = {
        "messages": messages,
        "is_valid": is_valid,
        "cookies": None
    }
    document = {
        "data": data,
        "links": links
    }
    if not verify_user(login, password):
        messages.append("Podano nieprawidłowy login lub hasło")
        is_valid = False
        data["is_valid"] = is_valid
        return document

    messages.append("Zalogowano!")
    payload = {
        "login": login,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    cookie = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    document["data"]["cookies"] = str(cookie, 'utf-8')
    return document


@app.route("/root/sender/dashboard", methods=['POST'])
def add_package():
    token = request.headers.get("cookie")
    data = {"is_authorized": False}
    if not is_authorized(data):
        return data

    package = request.json["package"]
    login = g.authorization["login"]

    packages = db.hget(f"user:{login}", "packages")
    if packages is None:
        package = json.dumps(package)
        db.hset(f"user:{login}", "packages", package)
        return data

    packages = json.loads(packages)
    new_packages = {**packages, **package}
    new_packages = json.dumps(new_packages)
    db.hset(f"user:{login}", "packages", new_packages)
    return data


@app.route("/root/carrier/dashboard", methods=['PUT'])
def put_carrier_dashboard():
    origin = request.headers.get('Origin')

    links = []
    links.append({"type": 'root:parent', "url": '/'})
    all_packages = {}
    packages_for_response = []
    data = {
        "is_authorized": False
    }
    document = {
        "data": data,
        "links": links
    }
    token = request.headers.get("auth_cookie")
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e:
        return document

    login = request.args.get('user')
    id = request.args.get('index_of_row')

    packages = json.loads(db.hget(f"user:{login}", "packages"))
    package = packages.get(id)

    print(package)
    old_state = package["state"]
    package["state"] = request.args.get('state')
    new_state = package["state"]

    new_packages = json.dumps(packages)
    db.hset(f"user:{login}", "packages", new_packages)

    adressee = package["adressee_name"]
    storeroom = package["storeroom_id"]
    size = package["size"]
    notification_text = f'''Zmieniono status paczki o adresacie: {adressee}, destynacji: {storeroom}
     i rozmiarze {size} z {old_state} na {new_state}'''
    db.lpush(f"notifications:{login}", notification_text)

    packages = json.loads(db.hget(f"user:{login}", "packages"))

    allowed_origins = ["http://localhost:3000",
                       "localhost", "http://localhost"]
    response = make_response(document, 200)
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin

    return response

@app.route("/root/sender/OA/createUser", methods=['POST'])
def OA_createUser():
    links = []
    links.append({"type": 'root:parent', "url": '/'})
    all_packages = {}
    packages_for_response = []
    data = {
        "is_authorized": False
    }
    document = {
        "data": data,
        "links": links
    }
    token = request.headers.get("cookie")
    try:
        g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e:
        return document
    data["is_authorized"] = True
    login = g.authorization.get('login')

    if not db.exists(f"user:{login}"):
        db.hset(f"user:{login}", "email", login)

    return document


@app.route("/root/sender/dashboard", methods=['DELETE'])
def del_packages():
    data = {"is_authorized": False}
    if not is_authorized(data):
        return data
    login = g.authorization["login"]

    db.hdel(f"user:{login}", "packages")
    return data


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000)
