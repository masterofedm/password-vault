import sqlite3
import os

from encryption import encrypt_password, decrypt_password


def get_db_path():

    base_path = os.path.join(
        os.getenv("LOCALAPPDATA"),
        "PasswordVault"
    )

    os.makedirs(base_path, exist_ok=True)

    return os.path.join(base_path, "passwords.db")


conn = sqlite3.connect(get_db_path())
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password BLOB,
    notes TEXT
)
""")

conn.commit()

def add_password(website, username, password, notes):
    encrypted = encrypt_password(password)

    cursor.execute(
        "INSERT INTO passwords (website, username, password, notes) VALUES (?, ?, ?, ?)",
        (website, username, encrypted, notes)
    )

    conn.commit()

def get_passwords():

    cursor.execute("SELECT website, username, password FROM passwords")
    rows = cursor.fetchall()

    result = []

    for row in rows:
        decrypted = decrypt_password(row[2])
        result.append((row[0], row[1], decrypted))

    return result

def delete_password(website):

    cursor.execute("DELETE FROM passwords WHERE website=?", (website,))
    conn.commit()

def search_password(term):

    cursor.execute(
        "SELECT website, username, password FROM passwords WHERE website LIKE ?",
        ('%' + term + '%',)
    )

    rows = cursor.fetchall()

    result = []

    for row in rows:
        decrypted = decrypt_password(row[2])
        result.append((row[0], row[1], decrypted))

    return result