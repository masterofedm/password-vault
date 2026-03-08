import unittest

from twofa import generate_secret, generate_totp, verify_totp, provisioning_uri


class TwoFATests(unittest.TestCase):
    def test_generate_secret_base32(self):
        secret = generate_secret()
        self.assertGreaterEqual(len(secret), 32)
        for ch in secret:
            self.assertIn(ch, "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")

    def test_totp_known_vector(self):
        # RFC 6238 (SHA1) with ASCII secret "12345678901234567890"
        # Base32 = GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ
        secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        code = generate_totp(secret, timestamp=59, digits=8)
        self.assertEqual(code, "94287082")

    def test_verify_totp(self):
        secret = "JBSWY3DPEHPK3PXP"
        now = 1700000000
        code = generate_totp(secret, timestamp=now)
        self.assertTrue(verify_totp(secret, code, timestamp=now, window=0))
        self.assertFalse(verify_totp(secret, "000000", timestamp=now, window=0))

    def test_provisioning_uri(self):
        uri = provisioning_uri("ABCDEF", "user1", "PasswordVault")
        self.assertIn("otpauth://totp/PasswordVault%3Auser1", uri)
        self.assertIn("secret=ABCDEF", uri)
        self.assertIn("issuer=PasswordVault", uri)


if __name__ == "__main__":
    unittest.main()
    