import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# User Table
c.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    is_admin INTEGER DEFAULT 0
);
"""
)

# ITEM Table
c.execute(
    """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""
)

# Create ADMIN USER with hashed password if not exists
admin_username = os.environ.get("INITIAL_ADMIN_USER", "admin")
admin_password = os.environ.get("INITIAL_ADMIN_PASSWORD", "ChangeMe!Admin123")

c.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
existing = c.fetchone()
if not existing:
    password_hash = generate_password_hash(admin_password)
    c.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)",
        (admin_username, password_hash),
    )

conn.commit()
conn.close()

print("Secure database initialized successfully.")
