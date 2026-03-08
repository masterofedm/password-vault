import tkinter as tk
from ui import PasswordManagerUI

APP_VERSION = "1.0"

root = tk.Tk()

app = PasswordManagerUI(root)

root.mainloop()