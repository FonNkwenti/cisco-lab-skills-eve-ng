#!/usr/bin/env python3
"""
Fault Injection Script Template: Missing Network Statement

Injects: Missing EIGRP Network Advertisement
Target Device: R1
Fault Type: Route Advertisement Error

This script connects to R1 via console and removes the network statement
for the Loopback0 interface, preventing it from being advertised to neighbors.
"""

from netmiko import ConnectHandler
import sys

# Device Configuration
DEVICE_NAME = "R1"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5001

# Fault Configuration Commands
FAULT_COMMANDS = [
    "router eigrp 100",
    "no network 1.1.1.1 0.0.0.0",
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
        print(f"[*] Removing Loopback0 network statement (FAULT)")
        output = conn.send_config_set(FAULT_COMMANDS)
        print(output)

        output = conn.save_config()
        print(output)

        conn.disconnect()

        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 3: Missing Network Statement is now active.")
        print(f"[!] R1's Loopback0 (1.1.1.1/32) will NOT be advertised to neighbors")

    except ConnectionRefusedError:
        print(f"[!] Error: Could not connect to {CONSOLE_HOST}:{CONSOLE_PORT}")
        print(f"[!] Make sure GNS3 is running and {DEVICE_NAME} is started.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("Fault Injection: Missing Network Statement")
    print("="*60)
    inject_fault()
    print("="*60)
