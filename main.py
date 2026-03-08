import socket
import sys

def single_instance():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", 65432))
    except socket.error:
        sys.exit()

single_instance()


import tkinter as tk
from ui import PasswordManagerUI

APP_VERSION = "1.5"

root = tk.Tk()

app = PasswordManagerUI(root)

root.mainloop()