from flaskext.mysql import MySQL
import sqlite3 as sql

USE_DB = None
mysql = None
app = None

SQLITE_DB = "sqlite.db"

def init(use_db, local_app=None):
    global USE_DB, app
    USE_DB = use_db
    if use_db == "MYSQL":
        app = local_app
        init_mysql()
    else:
        init_sqlite()


def get_conn():
    return mysql.connect() if USE_DB == "MYSQL" else sql.connect(SQLITE_DB)


def init_sqlite():
    create_login = """CREATE TABLE IF NOT EXISTS login (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(30) NOT NULL);"""
    delete_all = "DELETE FROM login"
    add_user = "INSERT INTO login(username, password) values('admin', 'admin');"
    con = get_conn()
    cur = con.cursor()
    cur.execute(create_login)
    cur.execute(delete_all)
    cur.execute(add_user)
    con.commit()
    con.close()


def init_mysql():
    global mysql
    mysql = MySQL()
    app.config['MYSQL_DATABASE_USER'] = 'root'
    app.config['MYSQL_DATABASE_PASSWORD'] = ''
    app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    app.config['MYSQL_DATABASE_DB'] = 'sqlinjection' # you first have to create id: CREATE DATABASE sqlinjection
    mysql.init_app(app)


    create_table ="""CREATE TABLE IF NOT EXISTS login (
                    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(30) NOT NULL,
                    password VARCHAR(30) NOT NULL);"""
    delete_table="DELETE FROM login";
    add_user = "INSERT INTO login(username, password) values('admin', 'admin');"
    add_user2 = "INSERT INTO login(username, password) values('hans', 'peter');"
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute(create_table)
    cursor.execute(delete_table)
    cursor.execute(add_user)
    cursor.execute(add_user2)
    con.commit()


def login(username, password, verbose):
    # for testing injection into SELECT. Exploitation blind or xpath (output in error msg)
    ret = "query: "
    cursor = get_conn()
    try:
        query = "SELECT * from login where username ='%s' and password ='%s'" % (username, password )
        ret += query + "\n"
        cursor.execute(query)
        ret += "Welcome\n" if cursor.fetchall() else "Invalid username or password\n"
    except Exception, e: 
        ret += "DB error: " + repr(e) + "\n" if verbose else ""
        ret += "Invalid username or password\n"
    return ret
        


def list_user(username, verbose):
    # for testing injection into SELECT. Exploitation with union all 
    ret = "query: "
    try:
        cursor = get_conn().cursor()
        query = "SELECT * from login where username = '%s'" % username #maybe: add a limit 1
        ret += query + "\n"
        cursor.execute(query)
        users = cursor.fetchall()
        ret += "DB response: " + str(users) + "\n"
    except Exception as e:
        ret += "DB error: " + repr(e) + "\n" if verbose else ""
    return ret
        

def add(username, password, verbose):
    # for testing injection into INSERT INTO
    ret = "query: "
    try:
        con = get_conn()
        cursor = con.cursor()
        query = "INSERT INTO login(username, password) values('%s', '%s')" % (username, password)
        ret += query + "\n"
        cursor.execute(query)
        con.commit()
        ret += "Done\n"
    except Exception as e:
        ret += "DB error: " + repr(e) + "\n" if verbose else ""
    return ret


def update(user_id, password, verbose):
    # for testing injection UPDATE 
    ret = "query: "
    try:
        con = get_conn()
        cursor = con.cursor()
        query = "UPDATE login SET password = '%s' WHERE id = %s" % (password, user_id)
        ret += query + "\n"
        cursor.execute(query)
        con.commit()
        ret += "Done\n"
    except Exception as e:
        ret += "DB error: " + repr(e) + "\n" if verbose else ""
    return ret


def delete(user_id, verbose):
    # for testing injection DELETE
    ret = "query: "
    try:
        con = get_conn()
        cursor = con.cursor()
        query = "DELETE FROM login where id = %s" % user_id
        ret += query + "\n"
        cursor.execute(query)
        con.commit()
        ret += "Done\n"
    except Exception as e:
        ret += "DB error: " + repr(e) + "\n" if verbose else ""
    return ret
