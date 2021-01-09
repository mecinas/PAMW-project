from flask import Flask, request, make_response, render_template, flash, jsonify, redirect, url_for, session
import requests
from os import getenv
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import jwt
from uuid import uuid4
import json
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException

#OA w kurierze
#Obsługiwanie kilku klientów na raz

load_dotenv()
SESSION_TYPE = 'filesystem'
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True

AUTH0_CALLBACK_URL = getenv('AUTH0_CALLBACK_URL')
AUTH0_CLIENT_ID = getenv('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = getenv('AUTH0_CLIENT_SECRET')
AUTH0_DOMAIN = getenv('AUTH0_DOMAIN')
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = getenv('AUTH0_AUDIENCE')
JWT_SECRET = getenv('JWT_SECRET')

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
app.debug = False
oauth = OAuth(app)
WEB_SERVICE_URL = "https://murmuring-springs-10121.herokuapp.com"

#Oauth section
auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    login = auth0.get('userinfo').json().get("name")

    payload = {
        "login": login,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    cookie = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    cookie = str(cookie, 'utf-8')

    url = WEB_SERVICE_URL + "/root/sender/OA/createUser"
    api_response = requests.post(url=url, headers={"cookie": cookie})

    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)
    api_response_data = json.loads(api_response.content)
    if not api_response_data.get("data").get("is_authorized"):
        return "Brak dostępu, aby przejść do tego panelu należy uprzednio się zalogować", 401

    response = make_response(render_template("home.html"))
    response.set_cookie('auth', cookie, max_age=200)

    return response

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/logout')
def logout():
    params = {'returnTo': url_for('open_logout', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
#

def get_respond_render(url, html_resource, cookie=None):
    api_response = requests.get(url)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)
    api_response_data = json.loads(api_response.content)
    client_response = make_response(render_template(html_resource))
    client_response.headers.set('links', api_response_data["links"])
    if cookie is not None:
        client_response.set_cookie('auth', cookie, max_age=200)
    return client_response

@app.route('/', methods=['GET'])
def open_home():
    url = WEB_SERVICE_URL + "/root"
    return get_respond_render(url, "home.html")

@app.route("/sender/register", methods=['GET'])
def open_register():
    url = WEB_SERVICE_URL + "/root/sender/register"
    return get_respond_render(url, "register.html")

@app.route("/sender/login", methods=['GET'])
def open_login():
    url = WEB_SERVICE_URL + "/root/sender/login"
    return get_respond_render(url, "login.html")

def get_authorized_render(url, html_resource, cookie, resources={}):
    api_response = requests.get(url=url, headers=cookie)

    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)
    api_response_data = json.loads(api_response.content)
    if not api_response_data.get("data").get("is_authorized"):
        return "Brak dostępu, aby przejść do tego panelu należy uprzednio się zalogować", 401

    client_response = make_response(render_template(html_resource, **resources))
    client_response.headers.set('links', api_response_data.get("links"))
    client_response.set_cookie('auth', cookie.get("cookie"), max_age=200)
    return client_response

@app.route("/sedner/notifications", methods=['GET'])
def open_notifications():
    url = WEB_SERVICE_URL + "/root/sender/notifications"
    cookie = {"cookie": request.cookies.get('auth')}

    return get_authorized_render(url, "notifications.html", cookie)

@app.route("/sender/notifications/update", methods=['GET'])
def update_notifications():
    url = WEB_SERVICE_URL + "/root/sender/notifications/update"
    cookie = {"cookie": request.cookies.get('auth')}
    api_response = requests.get(url=url, headers=cookie)

    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)
    api_response_data = json.loads(api_response.content).get("data")
    if not api_response_data.get("is_authorized"):
        return "Brak dostępu, aby przejść do tego panelu należy uprzednio się zalogować", 401
    return {"notification":api_response_data.get("notification")}


@app.route("/sender/dashboard", methods=['GET'])
def open_dashboard():
    url = WEB_SERVICE_URL + "/root/sender/dashboard"

    cookie = {"cookie": request.cookies.get('auth')}
    api_response = requests.get(url, headers=cookie)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)
    api_response_data = json.loads(api_response.content).get("data")
    resources = {
        "login": api_response_data["login"],
        "packages": api_response_data["packages"],
        "has_packages": api_response_data["has_packages"]
    }
    return get_authorized_render(url, "dashboard.html", cookie, resources)

@app.route("/sender/logout", methods=['GET'])
def open_logout():
    url = WEB_SERVICE_URL + "/root/sender/login"

    api_response = requests.get(url)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)

    api_response_data = json.loads(api_response.content)
    client_response = make_response(render_template("login.html"))
    client_response.headers.set('links', api_response_data["links"])
    client_response.delete_cookie('auth')
    flash("Wylogowano!")
    session.clear()
    return client_response

@app.route("/sender/register", methods=['POST'])
def register():
    data = {
        "firstname": request.form.get('firstname'),
        "lastname": request.form.get('lastname'),
        "email": request.form.get('email'),
        "adress": request.form.get('adress'),
        "login": request.form.get('login'),
        "password": request.form.get('password'),
        "sec_password": request.form.get('sec_password'),
    }

    url = WEB_SERVICE_URL + "/root/sender/register"
    api_response = requests.post(url, json=data)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)

    api_data = json.loads(api_response.content)
    for message in api_data["data"]["messages"]:
        flash(message)
    return get_respond_render(url,"register.html")

@app.route("/sender/login", methods=['POST'])
def post_login():
    data = {
        "login": request.form.get("login"),
        "password": request.form.get("password")
    }
    url = WEB_SERVICE_URL + "/root/sender/login"
    api_response = requests.post(url, json=data)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)

    api_data = json.loads(api_response.content)
    api_cookie = bytes(api_data["data"]["cookies"], 'utf-8')

    return get_respond_render(url, "login.html", cookie = api_cookie)

@app.route("/sender/dashboard", methods=['POST'])
def add_package():
    adressee_name = request.form.get("adressee_name")
    storeroom_id = request.form.get("storeroom_id")
    size = request.form.get("size")
    package = {
        str(uuid4()):
        {'adressee_name': adressee_name,
         "storeroom_id": storeroom_id,
         "size": size,
         "state": "Nadana"
         
         }
    }
    json = {
        "package": package
    }
    cookie = {"cookie": request.cookies.get('auth')}
    url = WEB_SERVICE_URL + "/root/sender/dashboard"
    api_response = requests.post(url=url, headers=cookie, json=json)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)

    return open_dashboard()

@app.route("/sender/dashboard/delete", methods=['POST'])
def add_packages():
    
    url = WEB_SERVICE_URL + "/root/sender/dashboard"
    cookie = {"cookie": request.cookies.get('auth')}
    api_response = requests.delete(url=url, headers=cookie)
    if(api_response.status_code >= 400):
        return make_response('Błąd w połączeniu z serwerem', 500)

    return open_dashboard()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
