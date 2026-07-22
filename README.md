# Network Recon Engine

A Python-based network port scanner built in two versions — a lightweight
socket-based scanner and an Nmap/Npcap-powered scanner with service and
version detection. Built as a hands-on cybersecurity portfolio project to
practice core network reconnaissance concepts used in real analyst workflows.

## Overview

This project started as a way to understand what tools like Nmap are
actually doing under the hood, before relying on the tool itself. It
includes two scanners:

- *`socket_scanner_basic.py`* — a pure-Python TCP connect scanner using
  the built-in `socket` library. No external dependencies required.
- **`npcap_scanner.py`** — a scanner built on top of the `python-nmap`
  library, using Nmap's SYN stealth scan (`-sS`) and service/version
  detection (`-sV`) to identify not just open ports, but what's actually
  running on them.

## Features

- Configurable target host and port range (supports single ports,
  comma-separated lists, and ranges like `1-1024`)
- Multithreaded scanning in the socket-based version for faster results
 on larger port ranges
- Per-port error handling — a single timeout or connection failure no
  longer crashes the entire scan
- Service and version fingerprinting via Nmap (e.g. identifying
  `Apache 2.4.41` running on an open port, not just "port 80 is open")
- Automatic timestamped report generation (`.txt`) for every scan,
  mirroring the kind of audit trail expected in real security work

## Requirements

**`socket_scanner_basic.py`**
- Python 3.x (no external libraries needed)

**`npcap_scanner.py`**
- Python 3.x
- [Nmap](https://nmap.org/download.html) installed and available on your
  system PATH
- `python-nmap` library: `pip install python-nmap`
- Windows users: [Npcap](https://npcap.com/) must be installed alongside
  Nmap, and the terminal should be run as Administrator for accurate
  SYN scan results

## Usage

```bash
python socket_scanner_basic.py
python npcap_scanner.py
```

You'll be prompted for a target host/IP and a port range. Results print
to the console and are saved automatically to a `.txt` report file.

## Example Output

Tested against a local machine (`127.0.0.1`) with a temporary HTTP
server running on port 8080:

Enter the target IP address or hostname to scan: 127.0.0.1
Scanning Target via Npcap Engine : 127.0.0.1
Host Status: UP

Port 21/tcp: closed (ftp)
Port 22/tcp: closed (ssh)
Port 80/tcp: closed (http)
Port 443/tcp: closed (https)
Port 8080/tcp: open (http, SimpleHTTPServer 0.6)

The scanner correctly identified port 8080 as open and fingerprinted the
exact service running on it, while every other checked port correctly
reported as closed — confirmed by re-running the scan after stopping the
service, which flipped port 8080 back to closed.

## Development Notes

This project went through a real debugging pass after initial development:

- Fixed a bug where a single port timeout in the socket-based scanner
  could raise an unhandled exception and terminate the entire scan
  before checking the remaining ports
- Added multithreading to speed up scans across larger port ranges
- Made the Windows-specific Nmap path detection conditional (`os.name`
  check) so the script doesn't assume a Windows environment
- Added the missing logic to actually parse and report per-port state
  and service/version data from Nmap's scan results — previously the
  script confirmed the host was up but never printed the port-level
  findings it had already collected

Full commit history reflects this progression from initial build to
fixed, tested version.

## Testing

All testing was performed against `127.0.0.1` (localhost) and
self-hosted local services (e.g. `python -m http.server`), which are
safe to scan without authorization concerns. No external or third-party
hosts were scanned without explicit permission.

## Roadmap

- Vulnerability scanner: cross-reference detected service/version data
  against known CVEs
- Basic log analyzer for detecting suspicious authentication activity
- Lightweight dashboard to visualize scan and log analysis results

## Author

Built by Abdallah Sani as part of ongoing cybersecurity skill-building,
including internship work with NITDA (National Information Technology
Development Agency).