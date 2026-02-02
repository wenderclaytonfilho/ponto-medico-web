from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

DB = "ponto_medico.db"


def get_db():
    return sqlite3.connect(DB)


def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS pontos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tipo TEXT,
        data TEXT
    )
    """)

    # Admin
    try:
        c.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)",
                  ("sebastiao.duque", "admin123", "admin"))
    except:
        pass

    db.commit()
    db.close()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    db = get_db()
    c = db.cursor()

    c.execute("SELECT id, role FROM users WHERE username=? AND password=?",
              (data["username"], data["password"]))
    user = c.fetchone()
    db.close()

    if user:
        session["user_id"] = user[0]
        session["role"] = user[1]
        return jsonify(success=True, role=user[1])

    return jsonify(success=False, message="Login inválido")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin.html")


@app.route("/registrar_ponto", methods=["POST"])
def registrar_ponto():
    if "user_id" not in session:
        return jsonify(error="não autorizado"), 403

    tipo = request.json["tipo"]
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO pontos VALUES (NULL, ?, ?, ?)",
              (session["user_id"], tipo, agora))
    db.commit()
    db.close()

    return jsonify(success=True)


@app.route("/meus_registros")
def meus_registros():
    db = get_db()
    c = db.cursor()

    c.execute("""
    SELECT tipo, data FROM pontos
    WHERE user_id=?
    ORDER BY id DESC
    """, (session["user_id"],))

    dados = [{"tipo": r[0], "data": r[1]} for r in c.fetchall()]
    db.close()

    return jsonify(dados)


@app.route("/relatorio")
def relatorio():
    if session.get("role") != "admin":
        return jsonify(error="não autorizado"), 403

    db = get_db()
    c = db.cursor()

    c.execute("""
    SELECT users.username, pontos.tipo, pontos.data
    FROM pontos
    JOIN users ON users.id = pontos.user_id
    ORDER BY pontos.data DESC
    """)

    dados = [{"username": r[0], "tipo": r[1], "data": r[2]} for r in c.fetchall()]
    db.close()

    return jsonify(dados)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
