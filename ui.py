import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import add_password, get_passwords, delete_password, search_password
import random
import string
import json
import requests

BG_COLOR = "#1e1e1e"
FRAME_COLOR = "#2d2d2d"
ENTRY_COLOR = "#3c3c3c"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#007acc"
BUTTON_TEXT = "#ffffff"

MASTER_PASSWORD = "admin123"


class PasswordManagerUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("650x450")
        self.root.configure(bg=BG_COLOR)

        self.create_menu()
        self.create_login()
        self.create_widgets()

        self.lock_timer = self.root.after(300000, self.auto_lock)

        self.root.bind_all("<Key>", lambda e: self.reset_timer())
        self.root.bind_all("<Button>", lambda e: self.reset_timer())

        self.check_for_updates()
        
    def check_for_updates(self):

        try:

            url = "https://raw.githubusercontent.com/YOURNAME/password-vault/main/version.txt"

            response = requests.get(url, timeout=5)

            latest_version = response.text.strip()

            from main import APP_VERSION

            if latest_version > APP_VERSION:

                from tkinter import messagebox

                if messagebox.askyesno(
                    "Update Available",
                    f"A new version ({latest_version}) is available.\nOpen download page?"
                ):

                    import webbrowser
                    webbrowser.open("https://github.com/YOURNAME/password-vault/releases")

        except:
            pass

    def lock_vault(self):

        self.root.withdraw()

        messagebox.showinfo("Vault Locked", "Vault has been locked.")

        self.create_login()

    def create_menu(self):

        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Backup", command=self.export_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        self.root.config(menu=menu_bar)


    def create_login(self):

        self.root.withdraw()

        login = tk.Toplevel()
        login.title("Unlock Vault")
        login.geometry("300x150")
        login.configure(bg=BG_COLOR)

        tk.Label(login, text="Enter Master Password", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

        entry = tk.Entry(login, show="*", bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground="white")
        entry.pack()

        def check():

            if entry.get() == MASTER_PASSWORD:
                login.destroy()
                self.root.deiconify()
                self.load_passwords()
            else:
                messagebox.showerror("Error", "Incorrect password")

        tk.Button(login, text="Unlock", command=check, bg=BUTTON_COLOR, fg=BUTTON_TEXT).pack(pady=10)


    def create_widgets(self):

        frame = tk.LabelFrame(self.root, text="Credentials", bg=FRAME_COLOR, fg=TEXT_COLOR, padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=10)

        tk.Label(frame, text="Website", bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=0, column=0)
        self.website = tk.Entry(frame, bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.website.grid(row=0, column=1)

        tk.Label(frame, text="Username", bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=1, column=0)
        self.username = tk.Entry(frame, bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.username.grid(row=1, column=1)

        tk.Label(frame, text="Password", bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=2, column=0)

        self.password = tk.Entry(frame, show="*", bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.password.grid(row=2, column=1)

        tk.Button(frame, text="👁", command=self.toggle_password, width=3).grid(row=2, column=2)

        self.password.bind("<KeyRelease>", self.update_strength)

        self.strength_label = tk.Label(frame, text="Strength:", bg=FRAME_COLOR, fg="white")
        self.strength_label.grid(row=2, column=3, padx=5)

        self.strength_bar = tk.Frame(frame, bg="#444", width=150, height=12)
        self.strength_bar.grid(row=2, column=4, padx=5)

        self.strength_fill = tk.Frame(self.strength_bar, bg="red", width=0, height=12)
        self.strength_fill.pack(side="left", fill="y")

        tk.Label(frame, text="Notes", bg=FRAME_COLOR, fg=TEXT_COLOR).grid(row=3, column=0)
        self.notes = tk.Entry(frame, bg=ENTRY_COLOR, fg=TEXT_COLOR, insertbackground="white")
        self.notes.grid(row=3, column=1)

        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Add", command=self.add, bg=BUTTON_COLOR, fg=BUTTON_TEXT, width=10).grid(row=0, column=0)
        tk.Button(button_frame, text="Delete", command=self.delete, bg=BUTTON_COLOR, fg=BUTTON_TEXT, width=10).grid(row=0, column=1)
        tk.Button(button_frame, text="Generate", command=self.generate, bg=BUTTON_COLOR, fg=BUTTON_TEXT, width=10).grid(row=0, column=2)
        tk.Button(button_frame, text="Search", command=self.search, bg=BUTTON_COLOR, fg=BUTTON_TEXT, width=10).grid(row=0, column=3)
        tk.Button(button_frame, text="Copy", command=self.copy, bg=BUTTON_COLOR, fg=BUTTON_TEXT, width=10).grid(row=0, column=4)
        tk.Button(button_frame, text="Lock", command=self.lock_vault, bg="#cc3300", fg="white", width=10).grid(row=0, column=5)

        columns = ("Website", "Username", "Password")

        self.table = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=200, anchor="center")

        self.table.pack(fill="both", expand=True)


    def check_strength(self, password):

        length = len(password)

        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()-_=+[]{};:,.<>?/|" for c in password)

        score = 0

        if length >= 12:
            score += 2
        elif length >= 8:
            score += 1

        if has_lower:
            score += 1
        if has_upper:
            score += 1
        if has_digit:
            score += 1
        if has_symbol:
            score += 1

        if score <= 2:
            return "Weak", "red", 40
        elif score <= 4:
            return "Medium", "orange", 90
        else:
            return "Strong", "green", 150


    def update_strength(self, event=None):

        password = self.password.get()

        strength, color, width = self.check_strength(password)

        self.strength_fill.config(bg=color, width=width)


    def add(self):
        add_password(self.website.get(), self.username.get(), self.password.get(), self.notes.get())
        self.load_passwords()


    def load_passwords(self):

        for row in self.table.get_children():
            self.table.delete(row)

        for row in get_passwords():
            self.table.insert("", tk.END, values=row)


    def delete(self):

        selected = self.table.selection()

        if not selected:
            return

        item = self.table.item(selected)
        website = item["values"][0]

        delete_password(website)

        self.load_passwords()


    def search(self):

        term = self.website.get()

        for row in self.table.get_children():
            self.table.delete(row)

        for row in search_password(term):
            self.table.insert("", tk.END, values=row)


    def copy(self):

        selected = self.table.selection()

        if not selected:
            return

        item = self.table.item(selected)
        password = item["values"][2]

        self.root.clipboard_clear()
        self.root.clipboard_append(password)

        messagebox.showinfo("Copied", "Password copied to clipboard")


    def generate(self):

        lower = random.choice(string.ascii_lowercase)
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        symbol = random.choice("!@#$%^&*()")

        others = ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*()") for _ in range(8))

        password = list(lower + upper + digit + symbol + others)
        random.shuffle(password)

        password = "".join(password)

        self.password.delete(0, tk.END)
        self.password.insert(0, password)

        # update strength bar
        self.update_strength()


    def toggle_password(self):

        if self.password.cget("show") == "*":
            self.password.config(show="")
        else:
            self.password.config(show="*")


    def export_backup(self):

        data = []

        for row in get_passwords():
            data.append({
                "website": row[0],
                "username": row[1],
                "password": row[2]
            })

        file = filedialog.asksaveasfilename(defaultextension=".pwm", filetypes=[("Password Manager Backup", "*.pwm")])

        if file:

            with open(file, "w") as f:
                json.dump(data, f, indent=4)

            messagebox.showinfo("Backup Created", "Backup saved successfully")


    def auto_lock(self):

        self.root.withdraw()
        messagebox.showinfo("Vault Locked", "Session timed out")
        self.create_login()


    def reset_timer(self):

        self.root.after_cancel(self.lock_timer)
        self.lock_timer = self.root.after(300000, self.auto_lock)