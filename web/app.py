from flask import Flask, request, make_response, render_template, flash, url_for, g
import requests
from redis import Redis
from os import getenv
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
from datetime import datetime
from jwt import encode, decode
from uuid import uuid4
import json

db = Redis(host='redis', port='6379', db=0)
load_dotenv()
SESSION_TYPE = 'filesystem'
SESSION_REDIS = db
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_HTTPONLY = True
JWT_SECRET = getenv("JWT_SECRET")
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
app.debug = False
WEB_SEVICE_URL = "https://murmuring-springs-10121.herokuapp.com"

def get_respond_render(url, html_resource, cookie=None):
    api_response = requests.get(url)
    api_response_data = json.loads(api_response.content)
    client_response = make_response(render_template(html_resource))
    client_response.headers.set('links', api_response_data["links"])
    if cookie is not None:
        client_response.set_cookie('auth', cookie, max_age=20)
    return client_response

@app.route('/', methods=['GET'])
def open_home():
    url = WEB_SEVICE_URL + "/root"
    return get_respond_render(url, "home.html")

@app.route("/sender/register", methods=['GET'])
def open_register():
    url = WEB_SEVICE_URL + "/root/sender/register"
    return get_respond_render(url, "register.html")

@app.route("/sender/login", methods=['GET'])
def open_login():
    url = WEB_SEVICE_URL + "/root/sender/login"
    return get_respond_render(url, "login.html")

@app.route("/sender/dashboard", methods=['GET'])
def open_dashboard():
    url = WEB_SEVICE_URL + "/root/sender/dashboard"

    api_response = requests.get(url, json=request.cookies.get('auth'))
    api_response_data = json.loads(api_response.content)
    return render_dashboard(api_response_data["data"], api_response_data["links"], "dashboard.html", request.cookies.get('auth'))

@app.route("/sender/logout", methods=['GET'])
def open_logout():
    url = WEB_SEVICE_URL + "/root/sender/login"
    api_response = requests.get(url)
    api_response_data = json.loads(api_response.content)
    client_response = make_response(render_template("login.html"))
    client_response.headers.set('links', api_response_data["links"])
    client_response.delete_cookie('auth')
    flash("Wylogowano!")
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

    url = WEB_SEVICE_URL + "/root/sender/register"
    api_response = requests.post(url, json=data)
    api_data = json.loads(api_response.content)
    for message in api_data["data"]["messages"]:
        flash(message)
    return get_respond_render(url,"register.html")

@app.route("/sender/login", methods=['POST'])
def login():
    data = {
        "login": request.form.get("login"),
        "password": request.form.get("password")
    }
    url = WEB_SEVICE_URL + "/root/sender/login"
    api_response = requests.post(url, json=data)
    api_data = json.loads(api_response.content)
    api_cookie = bytes(api_data["data"]["cookies"], 'utf-8')

    return get_respond_render(url, "login.html", cookie = api_cookie)

def render_dashboard(api_response_data, links, html_resource, cookie):
    if not api_response_data["is_authorized"]:
        return "Brak dostępu, aby przejść do tego panelu należy uprzednio się zalogować", 401
    if not api_response_data["has_packages"]:
        client_response = make_response(render_template("dashboard.html",
             login=api_response_data["login"], has_packages=False))
    else:
        client_response = make_response(render_template("dashboard.html",
             login=api_response_data["login"], packages=api_response_data["packages"], has_packages=True))
    client_response.headers.set('links', links)
    client_response.set_cookie('auth', cookie, max_age=20)
    return client_response

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
        "package": package,
        "cookie": request.cookies.get('auth')
    }
    url = WEB_SEVICE_URL + "/root/sender/dashboard"
    requests.post(url=url, json=json)

    return open_dashboard()

@app.route("/sender/dashboard/delete", methods=['POST'])
def add_packages():
    
    url = WEB_SEVICE_URL + "/root/sender/dashboard"
    cookie = request.cookies.get('auth')
    requests.delete(url=url, json=cookie)

    return open_dashboard()

if __name__ == '__main__':
    app.run()
