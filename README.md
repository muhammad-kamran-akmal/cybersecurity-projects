# Containerized Cybersecurity Lab Environment
> **Isolated Dual-Node Network Testbed for Cybersecurity Research and Education**

[![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue.svg)](https://www.docker.com/)
[![Compose](https://img.shields.io/badge/Docker_Compose-v2%2B-blue.svg)](https://docs.docker.com/compose/)
[![OS](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)](https://kernel.org/)
[![Status](https://img.shields.io/badge/Status-Phase%201%20Verified-success.svg)]()

---

## 1. Project Overview

This repository provides an ultra-lightweight, isolated, multi-node lab environment designed for cybersecurity research, network isolation experimentation, and hands-on security education.

Built using Docker and Docker Compose, the environment provisions an isolated virtual bridge network hosting two distinct Linux nodes:
- **`attacker` Node**: A minimal Kali Linux (`kalilinux/kali-rolling`) command-line container configured as the auditing/security assessment endpoint.
- **`target` Node**: A minimal Debian (`debian:bookworm-slim`) container serving as the target endpoint.

Both nodes reside on a dedicated custom Docker bridge network (`lab-network`), enabling deterministic DNS service resolution, packet routing, and network containment without exposing services to external networks.

---

## 2. Lab Topology & Architecture

```text
               Custom Docker Bridge Network (lab-network)
                                    │
               ┌────────────────────┴────────────────────┐
               │                                         │
      ┌────────▼────────┐                       ┌────────▼────────┐
      │    attacker     │                       │     target      │
      │    Container    │                       │    Container    │
      │                 │ ◄─── DNS Resolution ──►                 │
      │  Kali Linux     │   & Network Routing   │  Debian Linux   │
      │ (kali-rolling)  │                       │ (bookworm-slim) │
      └─────────────────┘                       └─────────────────┘
```

### Architectural Specifications:
- **Topology**: Exactly 2 isolated Linux containers on 1 custom bridge network.
- **Network Isolation**: User-defined bridge network (`lab-network`) providing automatic DNS discovery between containers.
- **Minimalist Design**: Zero unnecessary packages, no background services, no GUI overhead, and minimal resource footprint.

---

## 3. Repository Structure

```text
assignment1/
├── .agent/                    # Agent orchestration and synchronization files
│   ├── guide.md               # Assignment source requirements
│   ├── plan.md                # Project roadmap and milestone tracking
│   └── logs.md                # Execution and verification activity log
├── scripts/                   # Operational management scripts
│   ├── start.sh               # Starts the lab and triggers verification
│   ├── stop.sh                # Stops and removes the lab environment
│   └── verify_network.sh      # Automated health and reachability test suite
├── .gitignore                 # Standard repository ignore configuration
├── AGENT.md                   # Operational guidelines for autonomous agents
├── docker-compose.yml         # Container definitions and network specification
└── README.md                  # Comprehensive project documentation
```

---

## 4. Prerequisites

- **Docker Engine**: Version 20.10+ or later
- **Docker Compose**: Version 2.0+ (or Docker Compose plugin)
- **Operating System**: Linux, macOS, or Windows with WSL2

---

## 5. Quick Start Guide

### 1. Launch the Lab Environment
To build and initialize the containers in detached mode:
```bash
./scripts/start.sh
```
*Alternatively, use standard Docker Compose:*
```bash
docker compose up -d --build
```

### 2. Verify Network & Container Health
Run the automated verification suite to validate container status and inter-node DNS resolution:
```bash
./scripts/verify_network.sh
```

**Expected Verification Output:**
```text
======================================================
   Cybersecurity Lab: Environment Verification Test   
======================================================

 [*] Checking: Container 'attacker' is running... [PASS]
 [*] Checking: Container 'target' is running... [PASS]
 [*] Checking: Custom network 'lab-network' exists... [PASS]
 [*] Checking: 'attacker' connected to 'lab-network'... [PASS]
 [*] Checking: 'target' connected to 'lab-network'... [PASS]
 [*] Checking: 'attacker' resolves 'target'... [PASS]
 [*] Checking: 'target' resolves 'attacker'... [PASS]

--- Network Topology Details ---
 Attacker Container : attacker (IP: 172.21.0.2)
 Target Container   : target   (IP: 172.21.0.3)
 Bridge Network     : lab-network

[SUCCESS] All Phase 1 verification checks passed!
```

---

## 6. Accessing the Containers

Both containers are configured with interactive TTY support and a non-terminating foreground process (`sleep infinity`):

- **Access the `attacker` container:**
  ```bash
  docker compose exec attacker bash
  ```

- **Access the `target` container:**
  ```bash
  docker compose exec target bash
  ```

- **Inspect network connectivity between containers:**
  ```bash
  # Resolve target from attacker
  docker compose exec attacker getent hosts target

  # Resolve attacker from target
  docker compose exec target getent hosts attacker
  ```

---

## 7. Teardown & Clean Up

To gracefully stop and remove all containers and network resources:
```bash
./scripts/stop.sh
```
*Alternatively:*
```bash
docker compose down
```

---

## 8. Security & Containment Considerations

1. **Host Isolation**: Containers run within Docker's isolated namespaces, preventing lateral access to the host filesystem.
2. **Deterministic Resolution**: The custom bridge network utilizes Docker's internal embedded DNS server (`127.0.0.11`), eliminating reliance on external naming infrastructure.
3. **Controlled Scope**: Phase 1 enforces strict minimalism—no offensive tooling, listening daemons, or unverified packages are installed.

---

## License
Educational and research use only.
