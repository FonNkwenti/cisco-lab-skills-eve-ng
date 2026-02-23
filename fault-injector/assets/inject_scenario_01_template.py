#!/usr/bin/env python3
"""
Fault Injection Script Template: AS Number Mismatch

Injects: EIGRP AS Number Mismatch
Target Device: R2
Fault Type: Protocol Parameter Mismatch

This script connects to R2 via console and changes the EIGRP AS number
from 100 to 200, preventing adjacency formation with R1.
"""

from netmiko import ConnectHandler
import sys

# Device Configuration
DEVICE_NAME = "R2"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002

# Fault Configuration Commands
FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
    "eigrp router-id 2.2.2.2",
    "network 2.2.2.2 0.0.0.0",
    "network 10.0.12.0 0.0.0.3",
    "network 10.0.23.0 0.0.0.3",
    "passive-interface Loopback0",
    "no auto-summary",
]

def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Connecting to {DEVICE_NAME}...")

    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=CONSOLE_HOST,
            port=CONSOLE_PORT,
            username="",
            password="",
            secret="",
            timeout=10,
        )
        print(f"[+] Connected to {DEVICE_NAME}")

        print(f"[*] Injecting fault configuration...")
        print(f"[*] Changing EIGRP AS from 100 to 200 (FAULT)")
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)

        output = conn.save_config()
        print(output)

        conn.disconnect()

        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 1: AS Number Mismatch is now active.")
        print(f"[!] R2 will NOT form adjacency with R1 (AS mismatch)")

    except ConnectionRefusedError:
        print(f"[!] Error: Could not connect to {CONSOLE_HOST}:{CONSOLE_PORT}")
        print(f"[!] Make sure GNS3 is running and {DEVICE_NAME} is started.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("Fault Injection: AS Number Mismatch")
    print("="*60)
    inject_fault()
    print("="*60)
