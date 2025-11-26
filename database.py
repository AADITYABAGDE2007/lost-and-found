import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------
# ✅ Initialize database
# -------------------------
def init_db():
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Items table (with image column added)
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            reporter_name TEXT,
            contact TEXT,
            status TEXT CHECK(status IN ('lost', 'found', 'claimed')) DEFAULT 'lost',
            user_id INTEGER,
            image TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------
# ✅ Add a new user
# -------------------------
def add_user(username, password):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    hashed_password = generate_password_hash(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()


# -------------------------
# ✅ Verify login password
# -------------------------
def verify_password(username, password):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], password):
        return user  # returns full user row (id, username, password)
    return None


# -------------------------
# ✅ Add lost/found item (with optional image)
# -------------------------
def add_item(name, description, location, reporter_name, contact, status, user_id, image_filename=None):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO items (name, description, location, reporter_name, contact, status, user_id, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, location, reporter_name, contact, status, user_id, image_filename))
    conn.commit()
    conn.close()


# -------------------------
# ✅ Search items
# -------------------------
def search_items(query):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM items 
        WHERE name LIKE ? OR description LIKE ? OR location LIKE ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    results = c.fetchall()
    conn.close()
    return results


# -------------------------
# ✅ Get all items
# -------------------------
def get_all_items():
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.close()
    return items


# -------------------------
# ✅ Claim an item
# -------------------------
def claim_item(item_id):
    conn = sqlite3.connect('lost_and_found.db')
    c = conn.cursor()
    c.execute("UPDATE items SET status = 'claimed' WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
