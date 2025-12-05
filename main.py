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

# DASHBOARD (normal user)
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session or session.get("is_admin") == 1:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM items WHERE user_id={session['user_id']}")
    items = cur.fetchall()

    return render_template("dashboard.html", username=session["username"], items=items, total_items=len(items))

# ADD ITEM
@app.route("/add", methods=["GET", "POST"])
def add_item():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO items (user_id, title, content) VALUES (?, ?, ?)",
                    (session["user_id"], title, content))
        conn.commit()

        return redirect("/dashboard")

    return render_template("add_item.html")

# VIEW RECORD
@app.route("/view/<item_id>")
def view(item_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        f"SELECT items.*, users.username FROM items "
        f"JOIN users ON users.id = items.user_id WHERE items.id={item_id}"
    )
    record = cur.fetchone()

    return render_template("view_record.html", record=record)

# EDIT ITEM
@app.route("/edit/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM items WHERE id={item_id}")
    item = cur.fetchone()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cur.execute(f"UPDATE items SET title='{title}', content='{content}' WHERE id={item_id}")
        conn.commit()

        # admin returns to admin post list
        if session.get("is_admin") == 1:
            return redirect("/admin/posts")

        return redirect("/dashboard")

    return render_template("edit.html", rec=item)

# DELETE ITEM
@app.route("/delete/<item_id>")
def delete_item(item_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM items WHERE id={item_id}")
    conn.commit()

    if session.get("is_admin") == 1:
        return redirect("/admin/posts")

    return redirect("/dashboard")

