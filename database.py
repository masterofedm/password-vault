import sqlite3
from encryption import encrypt_password, decrypt_password

conn = sqlite3.connect("passwords.db")
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