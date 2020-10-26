from flask import Flask , render_template
app = Flask(__name__)
app.debug = False

@app.route('/')
def openHome():
    return render_template("home.html")

@app.route("/sender/sign-up")
def openRegister():
    return render_template("register.html")

app.run()