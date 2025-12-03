import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# User Table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    is_admin INTEGER DEFAULT 0
);
""")
# ITEM Table (dataset belongs to specific users)
c.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    content TEXT
);
""")

# Create ADMIN USER
try:
    c.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 1)")
except:
    pass

conn.commit()
conn.close()

print("Database created successfully.")
