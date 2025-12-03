from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site.db")

app = Flask(__name__)
app.secret_key = "vulnerable_app_key"  # intentionally weak

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    return redirect("/login")

# LOGIN section
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        # SQL injection kept intentionally
        cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
        user = cur.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]

            # if admin logs in, it goes to admin panel
            if user["is_admin"] == 1:
                return redirect("/admin")

            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")

# REGISTER section
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)",
                    (username, password))
        conn.commit()
        return redirect("/login")

    return render_template("register.html")
