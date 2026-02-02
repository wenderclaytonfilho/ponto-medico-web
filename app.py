from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "hospital-secret"

DB = "ponto.db"

# ---------------- DB ----------------
def conectar():
    return sqlite3.connect(DB, check_same_thread=False)

def criar_db():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        senha TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pontos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        tipo TEXT,
        datahora TEXT
    )
    """)

    con.commit()
    con.close()

# ---------------- USUÁRIOS ----------------
def criar_usuarios():
    medicos = [
        "adeilson.souza","alexandre.goncalves","andre.figueiredo",
        "antonio.ramos","antonio.viera","barbara.mendes",
        "camilla.germano","cesar.sousa","david.rodrigues",
        "duney.mendez","fabio.melo","fernando.luz",
        "hugo.costa","iara.ferreira","isabelly.cortez",
        "jaiflavio.lima","joao.pereira","jose.meneses",
        "jose.neto","jose.assis","kelly.sousa","kleyton.muniz",
        "landsteiner.leite","leticia.pinto","lucas.gomes",
        "lucas.pessoa","maria.rafael","mariana.valadares",
        "matheus.valadares","messias.mendes","osman.lira",
        "otacilio.cipriano","paloma.diniz","rayanne.cabral",
        "renata.marinho","renato.cavalcante","severina.amaral",
        "talles.amaral","thalyta.marques","yoandrys.hechavarria"
    ]

    con = conectar()
    cur = con.cursor()

    for m in medicos:
        cur.execute(
            "INSERT OR IGNORE INTO usuarios VALUES (NULL, ?, ?, 'user')",
            (m, "hrec*2026")
        )

    cur.execute(
        "INSERT OR IGNORE INTO usuarios VALUES (NULL, ?, ?, 'admin')",
        ("sebastiao.duque", "admin123")
    )

    con.commit()
    con.close()

# ---------------- ROTAS ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        senha = request.form["senha"]

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "SELECT role FROM usuarios WHERE username=? AND senha=?",
            (user, senha)
        )
        dados = cur.fetchone()
        con.close()

        if dados:
            session["user"] = user
            session["role"] = dados[0]
            return redirect("/admin" if dados[0] == "admin" else "/ponto")

    return render_template("login.html")

@app.route("/ponto", methods=["GET", "POST"])
def ponto():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        tipo = request.form["tipo"]
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO pontos VALUES (NULL, ?, ?, ?)",
            (session["user"], tipo, agora)
        )
        con.commit()
        con.close()

    con = conectar()
    cur = con.cursor()
    cur.execute(
        "SELECT tipo, datahora FROM pontos WHERE username=? ORDER BY datahora DESC",
        (session["user"],)
    )
    pontos = cur.fetchall()
    con.close()

    return render_template("ponto.html", pontos=pontos)

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/")

    medico = request.args.get("medico")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    query = "SELECT username, tipo, datahora FROM pontos WHERE 1=1"
    params = []

    if medico:
        query += " AND username=?"
        params.append(medico)

    if inicio:
        query += " AND date(datahora)>=?"
        params.append(inicio)

    if fim:
        query += " AND date(datahora)<=?"
        params.append(fim)

    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT DISTINCT username FROM pontos")
    medicos = [m[0] for m in cur.fetchall()]

    cur.execute(query + " ORDER BY datahora DESC", params)
    pontos = [
        {"username": p[0], "tipo": p[1], "datahora": p[2]}
        for p in cur.fetchall()
    ]

    con.close()

    return render_template("admin.html", pontos=pontos, medicos=medicos)

@app.route("/admin/relatorio", methods=["POST"])
def relatorio():
    medico = request.form.get("medico")
    inicio = request.form.get("inicio")
    fim = request.form.get("fim")

    con = conectar()
    cur = con.cursor()

    query = "SELECT username, tipo, datahora FROM pontos WHERE 1=1"
    params = []

    if medico:
        query += " AND username=?"
        params.append(medico)

    if inicio:
        query += " AND date(datahora)>=?"
        params.append(inicio)

    if fim:
        query += " AND date(datahora)<=?"
        params.append(fim)

    cur.execute(query, params)
    dados = cur.fetchall()
    con.close()

    arquivo = "relatorio_ponto.csv"
    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Médico", "Tipo", "Data/Hora"])
        writer.writerows(dados)

    return send_file(arquivo, as_attachment=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- MAIN ----------------
criar_db()
criar_usuarios()
if __name__ == "__main__":
    app.run()
