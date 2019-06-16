from flask import Flask, request
import db 
from ipdb import set_trace

app = Flask(__name__)

USE_DB = "MYSQL"
#USE_DB = "SQLITE"

@app.route("/")
def index():
    return "OK\n"


@app.route("/login")
def login():
    username = request.args.get('user')
    password = request.args.get('pass')
    if not all([username, password]):
        return "username or password empty\n"
    verbose = True if "verbose" in request.args else False
    print("got: ",username, password)
    return db.login(username, password, verbose)


@app.route("/list")
def list():
    username = request.args.get('user')
    verbose = True if "verbose" in request.args else False
    return db.list_user(username, verbose)
    

@app.route("/add")
def add():
    username = request.args.get('user')
    password = request.args.get('pass')
    if not all([username, password]):
        return "username or password empty\n"
    verbose = True if "verbose" in request.args else False
    return db.add(username, password, verbose)


@app.route("/del")
def delete():
    user_id = request.args.get('id')
    if not user_id:
        return "id is empty\n"
    verbose = True if "verbose" in request.args else False
    return db.delete(user_id, verbose)

@app.route("/update")
def update():
    user_id = request.args.get('id')
    password = request.args.get('pass')
    if not all([user_id, password]):
        return "id, username empty\n"
    verbose = True if "verbose" in request.args else False
    return db.update(user_id, password, verbose)


if __name__ == '__main__':
    db.init(USE_DB, app)
    app.run(host="0.0.0.0", debug=True)
