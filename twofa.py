import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import quote


def generate_secret(length=20):
    """Generate a Base32 secret suitable for TOTP apps like Duo Mobile."""
    random_bytes = os.urandom(length)
    return base64.b32encode(random_bytes).decode("utf-8").replace("=", "")


def _time_counter(timestamp=None, interval=30):
    if timestamp is None:
        timestamp = time.time()
    return int(timestamp // interval)


def generate_totp(secret, timestamp=None, digits=6, interval=30):
    """Generate a TOTP code for a given secret."""
    normalized = secret.strip().replace(" ", "").upper()
    padding = "=" * ((8 - len(normalized) % 8) % 8)
    key = base64.b32decode(normalized + padding)

    counter = _time_counter(timestamp, interval)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()

    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    code = binary % (10 ** digits)
    return str(code).zfill(digits)


def verify_totp(secret, code, timestamp=None, digits=6, interval=30, window=1):
    """Verify code allowing ±window intervals for clock drift."""
    if not code:
        return False

    cleaned = str(code).strip()
    if not cleaned.isdigit() or len(cleaned) != digits:
        return False

    if timestamp is None:
        timestamp = time.time()

    for step in range(-window, window + 1):
        candidate_time = timestamp + (step * interval)
        if hmac.compare_digest(generate_totp(secret, candidate_time, digits, interval), cleaned):
            return True

    return False


def provisioning_uri(secret, account_name, issuer="PasswordVault"):
    """Create an otpauth URI that Duo Mobile can scan/import."""
    label = quote(f"{issuer}:{account_name}")
    encoded_issuer = quote(issuer)
    return (
        f"otpauth://totp/{label}?secret={secret}&issuer={encoded_issuer}"
        "&algorithm=SHA1&digits=6&period=30"
    )
