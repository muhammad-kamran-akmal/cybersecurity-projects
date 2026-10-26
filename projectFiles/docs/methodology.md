# Methodology

We follow a simplified version of the **Cyber Kill Chain** / **MITRE ATT&CK**
phases, restricted to what can be demonstrated in a single isolated lab.

1. **Reconnaissance** — `nmap -sV -p 22 target` to fingerprint the SSH
   service and OS.
2. **Weaponisation** — build `encrypter.py` / `extractor.py` (Fernet).
3. **Delivery** — `scp` the payload over the already-compromised SSH session.
4. **Exploitation** — log in via weak credentials (`root:toor`) enabled by
   `PermitRootLogin yes`.
5. **Installation** — payload staged at `/tmp/encrypter.py`.
6. **Command & Control** — out of scope (attacker acts interactively).
7. **Actions on Objective** — encrypt `/home/*`, drop `README.md`, demand
   $5000 to `cryptoABC`.

Ethical note: the entire chain runs on a private Docker bridge network with
no route to the host LAN or the internet (aside from apt during build).
