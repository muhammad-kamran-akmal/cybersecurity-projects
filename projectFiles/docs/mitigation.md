# Mitigations

## SSH hardening
- `PermitRootLogin no`
- `PasswordAuthentication no` (keys only)
- `MaxAuthTries 3`
- Move to a non-default port, restrict by source IP

## Account security
- Strong password policy + password manager
- MFA on admin accounts
- Regular credential rotation

## Endpoint
- File integrity monitoring (`auditd`, AIDE, Wazuh)
- Immutable / offline backups (3-2-1 rule)
- Least privilege — services should not run as root

## Detection
- Alert on mass file renames to a common extension
- Alert on new `README*` files in user directories
- Alert on unusual outbound SSH from servers
- Centralise logs to a SIEM

## Response (if prevention fails)
1. Isolate the host from the network.
2. Preserve memory + disk for forensics.
3. Identify the encryption scheme (here: Fernet with derived key).
4. Restore from clean backup rather than paying.
5. Report to relevant authorities (NCSC / Action Fraud).
