import jwt
from flask import redirect, render_template, app, session, url_for, flash, Flask, request, send_file
from constant import *
import datetime
import sqlite3
import os
from pdf_writer import *
import matplotlib.pyplot as plt
plt.close('all')
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['SECRET_KEY'] = SECRET_KEY
app.permanent_session_lifetime = datetime.timedelta(days=90)


def get_db_connection():
    conn = sqlite3.connect(os.path.join('database/data.db'))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur


@app.route("/", methods=["POST", "GET"])
def index():
    if not session:
        error_id = 0
        if request.method == "POST":
            login = request.form["login"]
            cod = request.form["code"]
            if not login:
                error_id = 1
            elif not cod:
                error_id = 2
            else:
                conn, cur = get_db_connection()
                cur.execute("SELECT * FROM users where login = (?)", (login,))
                row = cur.fetchone()
                conn.close()
                if not row:
                    error_id = 3
                else:
                    code = jwt.decode(row["cod"], app.config["SECRET_KEY"], algorithms=['HS256'])["code"]
                    if code == cod:
                        session["login"] = login
                        session["promis"] = int(row["promis"])
                        return redirect(url_for('home'))
        return render_template("index.html", error_id=error_id)
    else:
        return redirect(url_for('home'))


@app.route("/home", methods=["POST", "GET"])
def home():
    if not session:
        return redirect(url_for("index"))
    return render_template("home.html", promis=int(session["promis"]), login=session["login"])


@app.route("/edit_akk", methods=["POST", "GET"])
def edit():
    error = []
    if not session:
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form["btn"] == "login":
            login = str(request.form["login"])
            code = str(request.form["code"])
            if not login:
                error.append(1)
                error.append('логин')
            elif not code:
                error.append(1)
                error.append("пароль")
            else:
                conn, cur = get_db_connection()
                test_login = cur.execute("SELECT * FROM users where login = (?)", (login,)).fetchone()
                if test_login is not None:
                    error.append(2)
                else:
                    now_user = cur.execute("SELECT * FROM users WHERE login = (?)", (session["login"],)).fetchone()
                    old_code = jwt.decode(now_user["cod"], app.config["SECRET_KEY"], algorithms=["HS256"])
                    if old_code["code"] != code:
                        error.append(3)
                    else:
                        cur.execute("UPDATE users SET login = (?) WHERE login = (?)", (login, session["login"]))
                        session["login"] = login
                        conn.commit()
                        conn.close()
                        return redirect(url_for("home"))
        elif request.form["btn"] == "code":
            new_code = str(request.form["new_code"])
            old_code = str(request.form["old_code"])
            if not new_code:
                error.append(1)
                error.append('новый пароль')
            elif not old_code:
                error.append(1)
                error.append("страый пароль")
            else:
                conn, cur = get_db_connection()
                now_user = cur.execute("SELECT * FROM users WHERE login=(?)", (session["login"],)).fetchone()
                rold_code = jwt.decode(now_user["cod"], app.config["SECRET_KEY"], algorithms=["HS256"])
                if rold_code["code"] != old_code:
                    error.append(3)
                else:
                    new_code = jwt.encode({"code":new_code}, app.config["SECRET_KEY"], algorithm="HS256")
                    cur.execute("UPDATE users SET cod = (?) WHERE login = (?)", (new_code, session["login"],))
                    conn.commit()
                    conn.close()
                    return redirect(url_for("home"))
    return render_template("edit_akk.html", error=error)


@app.route("/registor_akk", methods=['GET', 'POST'])
def registor():
    error = []
    if not session:
        return redirect(url_for("index"))
    if session["promis"] != 0 and session["promis"] != 1:
        return redirect(url_for("home"))
    if request.method == "POST":
        if request.form["btn"] == "reg":
            login = request.form["login"]
            code = request.form["code"]
            promis = request.form["promis"]
            if not login:
                error.append(1)
                error.append("логин")
            elif not code:
                error.append(1)
                error.append("пароль")
            elif not promis:
                error.append(1)
                error.append("права")
            else:
                conn, cur = get_db_connection()
                temp_user = cur.execute("SELECT * FROM users WHERE login = (?)", (login,)).fetchone()
                if temp_user is not None:
                    error.append(2)
                else:
                    code = jwt.encode({"code":code}, app.config["SECRET_KEY"], algorithm="HS256")
                    cur.execute("INSERT INTO users (login, cod, promis) VALUES (?, ?, ?)", (login, code, promis,))
                    conn.commit()
                conn.close()
        elif request.form["btn"] == "promis":
            login = request.form["login1"]
            promis = request.form["promis1"]
            if not login:
                error.append(1)
                error.append("логин")
            elif not promis:
                error.append(1)
                error.append("права")
            else:
                conn, cur = get_db_connection()
                temp_user = cur.execute("SELECT * FROM users WHERE login = (?)", (login,)).fetchone()
                if temp_user is None:
                    error.append(3)
                else:
                    cur.execute("UPDATE users SET promis = (?) WHERE login = (?)", (promis, login))
                    conn.commit()
                conn.close()
    return render_template("edit_user.html", error=error)


@app.route("/add_product", methods=["POST", "GET"])
def add_product():
    if not session:
        return redirect(url_for("index"))
    if session["promis"] == 1:
        return redirect(url_for("home"))
    error = []
    conn, cur = get_db_connection()
    storages = [i['name'] for i in cur.execute('SELECT name FROM storage').fetchall()]
    types = [i['name'] for i in cur.execute("SELECT name FROM type_product").fetchall()]

    if request.method == "POST":
        if request.form["bnt"] == "product":
            quantity = request.form["quantity"]
            type = request.form["type"]
            storage = request.form["storage"]
            if not quantity:
                error.append(1)
            try:
                quantity = int(quantity)
            except ValueError:
                error.append(3)
            else:
                row = cur.execute("SELECT * FROM products WHERE type = (?) AND storage = (?)", (type, storage,)).fetchone()
                temp = cur.execute("SELECT * FROM storage WHERE name = (?)", (storage,)).fetchone()
                if temp["сapacity"] - quantity < 0:
                    error.append(5)
                else:
                    cur.execute("UPDATE storage SET сapacity = (?) WHERE name = (?)",
                                (temp["сapacity"] - quantity, storage,))
                    if row is not None:
                        new_ctn = row["count"] + quantity
                        if new_ctn <= 0:
                            error.append(4)
                        else:
                            cur.execute("UPDATE products SET count = (?) WHERE type = (?) AND storage = (?)", (new_ctn, type, storage,))
                            conn.commit()
                    else:
                        if quantity <= 0:
                            error.append(4)
                        else:
                            cur.execute("INSERT INTO products (type, count, storage) VALUES (?,?,?)", (type, quantity, storage))
                            conn.commit()

        elif request.form["bnt"] == "new_type":
            type = request.form["new_type"]
            temp = cur.execute('SELECT * FROM type_product WHERE name = (?)', (type,)).fetchone()
            if temp is not None:
                error.append(2)
            else:
                cur.execute("INSERT INTO type_product (name) VALUES (?)", (type,))
                types.append(type)
                conn.commit()
    conn.close()
    return render_template("add_product.html", storages=storages, types=types, error=error)


@app.route("/edit_storage", methods=["POST", "GET"])
def edit_storage():
    if not session:
        return redirect(url_for("index"))
    if session["promis"] != 0 and session["promis"] != 3:
        return redirect(url_for("home"))
    error = []
    conn, cur = get_db_connection()
    storages = [i['name'] for i in cur.execute('SELECT name FROM storage').fetchall()]
    if request.method == "POST":
        if request.form["btn"] == "create":
            name = request.form["name"]
            address = request.form["address"]
            сapacity = request.form["сapacity"]

            if not name:
                error.append(1)
                error.append("имя")
            elif not address:
                error.append(1)
                error.append("адрес")
            elif not сapacity:
                error.append(1)
                error.append("количество")
            else:

                try:
                    сapacity = int(сapacity)
                except ValueError:
                    error.append(2)
                else:
                    if сapacity <= 0:
                        error.append(2)
                    else:
                        temp = cur.execute("SELECT * FROM storage WHERE name = (?);", (name,)).fetchone()
                        if temp is not None:
                            error.append(3)
                        else:
                            cur.execute("INSERT INTO storage (name, address, сapacity, сapacity2) VALUES (?,?,?,?)", (name, address, сapacity,сapacity,))
                            conn.commit()
                            storages.append(name)
        elif request.form["btn"] == "update":
            name = request.form["name1"]
            сapacity = request.form["сapacity1"]
            if not name:
                error.append(1)
                error.append("имя")
            elif not сapacity:
                error.append(1)
                error.append("количество")
            else:
                try:
                    сapacity = int(сapacity)
                except:
                    error.append(2)
                else:
                    if сapacity <= 0:
                        error.append(2)
                    else:
                        row = cur.execute("SELECT * FROM storage where name = (?)", (name,)).fetchone()
                        difference = сapacity-row["сapacity2"]
                        if difference < 0:
                            if row["сapacity"]+difference <0:
                                error.append(4)
                            else:
                                cap = row["сapacity"] + difference
                                cur.execute("UPDATE storage SET сapacity=(?), сapacity2=(?) WHERE name=(?)",
                                            (cap, сapacity, name,))
                                conn.commit()
                        else:
                            cap = row["сapacity"] + difference
                            cur.execute("UPDATE storage SET сapacity=(?), сapacity2=(?) WHERE name=(?)", (cap, сapacity, name,))
                            conn.commit()
    conn.close()
    return render_template("edit_storage.html", storages=storages, error=error)


@app.route('/give_report', methods=["GET"])
def give_report():
    if not session:
        return redirect(url_for("index"))
    if session["promis"] == 1:
        return redirect(url_for("home"))
    plt.close('all')
    if report() != 200:
        return "Что-то сломалось"
    return render_template("give_report.html")


@app.route('/download')
def download():
    path = 'temp/report.pdf'
    return send_file(path, as_attachment=True)


@app.route("/exit", methods=['GET', 'POST'])
def exit_fun():
    if request.method == 'POST':
        session.clear()
        return redirect("/", 301)
    return render_template("exit.html")


if __name__ == '__main__':
    app.run(debug=False)
