This is my first actual running app on PC!
 
 This app can
 -store saved passwords
 -import passwords
 -export passwords
 -be able to search your saved passwords
 -generate random passwords using encryption
 -times out after no activity
 -able to copy passwords as well
+-support Duo Mobile 2FA (TOTP) on vault login
 
 -- main login is admin123
 
+## Duo Mobile 2FA setup
+1. Open the app and go to **Security -> Enable Duo Mobile 2FA**.
+2. In Duo Mobile, add a third-party account.
+3. Use the secret shown in the app (it is also copied to clipboard).
+4. On next unlock, enter your master password and then your 6-digit Duo code.
+
+A local `vault_settings.json` file stores whether 2FA is enabled and your TOTP secret.
 
+---will provide future updates to hopefully bring this to phones and make it look more professional on desktop---
