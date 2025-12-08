import os
import sqlite3
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    abort,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site.db")

app = Flask(__name__)

# Strong secret key loaded from environment
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", os.urandom(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            abort(403)
        return view_func(*args, **kwargs)

    return wrapper

def get_current_user():
    if "user_id" not in session:
        return None
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin FROM users WHERE id = ?", (session["user_id"],))
    return cur.fetchone()

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# LOGIN section
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        cur = conn.cursor()
        # Parameterized query, look up by username only
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            # Regenerate session
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])

            if session["is_admin"]:
                return redirect(url_for("admin_panel"))
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")

# REGISTER section
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "warning")
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)",
                (username, password_hash),
            )
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")

    return render_template("register.html")

# DASHBOARD (normal user)
@app.route("/dashboard")
@login_required
def dashboard():
    # Only non-admin dashboard
    if session.get("is_admin"):
        return redirect(url_for("admin_panel"))

    conn = get_db()
    cur = conn.cursor()
    # Parameterized query, user_id from session
    cur.execute("SELECT id, title FROM items WHERE user_id = ?", (session["user_id"],))
    items = cur.fetchall()

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        items=items,
        total_items=len(items),
    )

# ADD ITEM
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title:
            flash("Title is required.", "warning")
            return render_template("add_item.html")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (user_id, title, content) VALUES (?, ?, ?)",
            (session["user_id"], title, content),
        )
        conn.commit()

        flash("Item added.", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_item.html")

def get_item_or_404(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT items.id, items.user_id, items.title, items.content, users.username "
        "FROM items JOIN users ON users.id = items.user_id WHERE items.id = ?",
        (item_id,),
    )
    item = cur.fetchone()
    if item is None:
        abort(404)
    return item

def ensure_can_access_item(item):
    """Non-admins can only access their own items."""
    if session.get("is_admin"):
        return
    if item["user_id"] != session.get("user_id"):
        abort(403)

# VIEW RECORD
@app.route("/view/<int:item_id>")
@login_required
def view(item_id):
    item = get_item_or_404(item_id)
    ensure_can_access_item(item)
    return render_template("view_record.html", record=item)

# EDIT ITEM
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = get_item_or_404(item_id)
    ensure_can_access_item(item)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title:
            flash("Title is required.", "warning")
            return render_template("edit.html", rec=item)

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE items SET title = ?, content = ? WHERE id = ?",
            (title, content, item_id),
        )
        conn.commit()

        flash("Item updated.", "success")
        if session.get("is_admin"):
            return redirect(url_for("admin_posts"))
        return redirect(url_for("dashboard"))

    return render_template("edit.html", rec=item)

# DELETE ITEM
@app.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    item = get_item_or_404(item_id)
    ensure_can_access_item(item)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()

    flash("Item deleted.", "info")
    if session.get("is_admin"):
        return redirect(url_for("admin_posts"))
    return redirect(url_for("dashboard"))

# ADMIN PANEL – home
@app.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("admin_home.html")


@app.route("/admin/posts")
@login_required
@admin_required
def admin_posts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT items.id, items.title, items.content, users.username "
        "FROM items JOIN users ON items.user_id = users.id"
    )
    posts = cur.fetchall()
    return render_template("admin_posts.html", posts=posts)

# ADMIN – USERS LIST
@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin FROM users")
    users = cur.fetchall()
    return render_template("admin_users.html", users=users)

# ADMIN DELETE USER
@app.route("/admin/delete_user/<int:uid>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(uid):
    # Prevent deleting self (optional)
    if uid == session.get("user_id"):
        flash("You cannot delete your own admin account.", "warning")
        return redirect(url_for("admin_users"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ? AND is_admin = 0", (uid,))
    conn.commit()

    flash("User deleted.", "info")
    return redirect(url_for("admin_users"))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":

    app.run(debug=True)
