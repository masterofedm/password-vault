import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from cryptography.fernet import Fernet
import os
import random
import string

MASTER_PASSWORD = "admin123"

# -----------------------------
# Encryption Key Setup
# -----------------------------

def load_key():
    return open("secret.key", "rb").read()

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Create key if it doesn't exist
if not os.path.exists("secret.key"):
    generate_key()

# Load the saved key
key = load_key()
cipher = Fernet(key)


# -----------------------------
# Database Setup
# -----------------------------

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

# -----------------------------
# Functions
# -----------------------------

def add_entry():

    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    notes = notes_entry.get()

    if website == "" or password == "":
        messagebox.showerror("Error", "Website and password required")
        return

    encrypted_password = cipher.encrypt(password.encode())

    cursor.execute(
        "INSERT INTO passwords (website, username, password, notes) VALUES (?, ?, ?, ?)",
        (website, username, encrypted_password, notes)
    )

    conn.commit()

    load_passwords()
    clear_fields()


def load_passwords():

    for row in password_table.get_children():
        password_table.delete(row)

    cursor.execute("SELECT website, username, password FROM passwords")
    rows = cursor.fetchall()

    for row in rows:

        decrypted_password = cipher.decrypt(row[2]).decode()

        password_table.insert(
            "", tk.END,
            values=(row[0], row[1], decrypted_password)
        )


def delete_entry():

    selected = password_table.selection()

    if not selected:
        return

    item = password_table.item(selected)
    website = item["values"][0]

    cursor.execute("DELETE FROM passwords WHERE website=?", (website,))
    conn.commit()

    load_passwords()


def clear_fields():

    website_entry.delete(0, tk.END)
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)


def generate_password():

    length = 12

    characters = string.ascii_letters + string.digits + "!@#$%^&*()"

    password = "".join(random.choice(characters) for _ in range(length))

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

def login():

    login_window = tk.Toplevel()
    login_window.title("Unlock Password Vault")
    login_window.geometry("300x150")
    login_window.resizable(False, False)

    tk.Label(login_window, text="Enter Master Password").pack(pady=10)

    password_entry = tk.Entry(login_window, show="*", width=25)
    password_entry.pack(pady=5)

    def check_password():

        if password_entry.get() == MASTER_PASSWORD:
            login_window.destroy()
            root.deiconify()
        else:
            messagebox.showerror("Error", "Incorrect Password")

    tk.Button(login_window, text="Unlock", command=check_password).pack(pady=10)

def copy_password():

    selected = password_table.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select a password first")
        return

    item = password_table.item(selected)
    password = item["values"][2]

    root.clipboard_clear()
    root.clipboard_append(password)

    messagebox.showinfo("Copied", "Password copied to clipboard")

def search_entry():

    search_term = website_entry.get()

    for row in password_table.get_children():
        password_table.delete(row)

    cursor.execute(
        "SELECT website, username, password FROM passwords WHERE website LIKE ?",
        ('%' + search_term + '%',)
    )

    rows = cursor.fetchall()

    for row in rows:

        decrypted_password = cipher.decrypt(row[2]).decode()

        password_table.insert("", tk.END, values=(row[0], row[1], decrypted_password))


# -----------------------------
# Main Window
# -----------------------------

root = tk.Tk()
root.withdraw()
root.title("Password Manager")
root.geometry("650x450")
root.resizable(False, False)

# -----------------------------
# Input Frame
# -----------------------------

input_frame = tk.LabelFrame(root, text="Add / Edit Credentials", padx=10, pady=10)
input_frame.pack(fill="x", padx=10, pady=10)

tk.Label(input_frame, text="Website").grid(row=0, column=0, sticky="w")
website_entry = tk.Entry(input_frame, width=30)
website_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Username / Email").grid(row=1, column=0, sticky="w")
username_entry = tk.Entry(input_frame, width=30)
username_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Password").grid(row=2, column=0, sticky="w")
password_entry = tk.Entry(input_frame, width=30, show="*")
password_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Notes").grid(row=3, column=0, sticky="w")
notes_entry = tk.Entry(input_frame, width=30)
notes_entry.grid(row=3, column=1, padx=5, pady=5)

# -----------------------------
# Button Frame
# -----------------------------

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(button_frame, text="Add Entry", width=15, command=add_entry).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Delete Entry", width=15, command=delete_entry).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Generate Password", width=18, command=generate_password).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Clear Fields", width=15, command=clear_fields).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="Copy Password", width=18, command=copy_password).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="Search", width=12, command=search_entry).grid(row=1, column=0, pady=5)

# -----------------------------
# Table Frame
# -----------------------------

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Website", "Username", "Password")

password_table = ttk.Treeview(table_frame, columns=columns, show="headings")

for col in columns:
    password_table.heading(col, text=col)
    password_table.column(col, width=200)

password_table.pack(fill="both", expand=True)

# -----------------------------
# Load Existing Passwords
# -----------------------------

load_passwords()

# -----------------------------
# Run Program
# -----------------------------
login()

root.mainloop()

conn.close()