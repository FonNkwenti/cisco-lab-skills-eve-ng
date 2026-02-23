#!/usr/bin/env python3
"""
Fault Injection Script Template: Passive Interface Misconfiguration

Injects: Passive Interface Default with Wrong Exclusion
Target Device: R3
Fault Type: Interface Configuration Error

This script connects to R3 via console and configures passive-interface default,
then incorrectly excludes Loopback0 instead of the transit interface, preventing
adjacency formation with R2.
"""

from netmiko import ConnectHandler
import sys

# Device Configuration
DEVICE_NAME = "R3"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5003

# Fault Configuration Commands
FAULT_COMMANDS = [
    "router eigrp 100",
    "passive-interface default",
    "no passive-interface Loopback0",
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
        print(f"[*] Configuring passive-interface default (FAULT)")
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)

        output = conn.save_config()
        print(output)

        conn.disconnect()

        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 2: Passive Interface Misconfiguration is now active.")
        print(f"[!] R3 will NOT form adjacency with R2 (all interfaces passive)")

    except ConnectionRefusedError:
        print(f"[!] Error: Could not connect to {CONSOLE_HOST}:{CONSOLE_PORT}")
        print(f"[!] Make sure GNS3 is running and {DEVICE_NAME} is started.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("Fault Injection: Passive Interface Misconfiguration")
    print("="*60)
    inject_fault()
    print("="*60)
