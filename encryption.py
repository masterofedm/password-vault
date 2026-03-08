from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

if not os.path.exists(KEY_FILE):
    generate_key()

cipher = Fernet(load_key())

def encrypt_password(password):
    return cipher.encrypt(password.encode())

def decrypt_password(encrypted):
    return cipher.decrypt(encrypted).decode()