#!/usr/bin/env python3
"""
Solution Restoration Script Template

Restores all devices to their correct EIGRP configuration,
removing all injected faults from troubleshooting scenarios.

This script connects to all active devices and applies the
correct configuration from the lab solutions.
"""

from netmiko import ConnectHandler
import sys

# EVE-NG server IP — update to match your environment
EVE_NG_HOST = "192.168.x.x"

# Device Console Mappings — ports are dynamic (from EVE-NG web UI / Console Access Table)
DEVICES = {
    "R1": {"host": EVE_NG_HOST, "port": 32768},
    "R2": {"host": EVE_NG_HOST, "port": 32769},
    "R3": {"host": EVE_NG_HOST, "port": 32770},
}

# Correct EIGRP Configuration per Device
CONFIGS = {
    "R1": [
        "no router eigrp 200",  # Remove any wrong AS
        "router eigrp 100",
        "eigrp router-id 1.1.1.1",
        "network 1.1.1.1 0.0.0.0",
        "network 10.0.12.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
    "R2": [
        "no router eigrp 200",  # Remove any wrong AS
        "router eigrp 100",
        "eigrp router-id 2.2.2.2",
        "network 2.2.2.2 0.0.0.0",
        "network 10.0.12.0 0.0.0.3",
        "network 10.0.23.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
    "R3": [
        "router eigrp 100",
        "no passive-interface default",  # Remove passive default
        "eigrp router-id 3.3.3.3",
        "network 3.3.3.3 0.0.0.0",
        "network 10.0.23.0 0.0.0.3",
        "passive-interface Loopback0",
        "no auto-summary",
    ],
}

def restore_device(device_name, config):
    """Restore a single device to correct configuration."""
    host = DEVICES[device_name]["host"]
    port = DEVICES[device_name]["port"]

    print(f"\n[*] Restoring {device_name} ({host}:{port})...")

    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=host,
            port=port,
            username="",
            password="",
            secret="",
            timeout=10,
        )
        print(f"[+] Connected to {device_name}")

        output = conn.send_config_set(config)
        print(output)

        output = conn.save_config()
        print(output)

        print(f"[+] {device_name} restored successfully!")
        conn.disconnect()
        return True

    except ConnectionRefusedError:
        print(f"[!] Error: Could not connect to {device_name} at {host}:{port}")
        print(f"[!] Make sure the EVE-NG lab is running and {device_name} is started.")
        return False
    except Exception as e:
        print(f"[!] Error on {device_name}: {e}")
        return False

def main():
    """Restore all devices to correct configuration."""
    print("="*60)
    print("Solution Restoration: Removing All Faults")
    print("="*60)

    success_count = 0
    fail_count = 0

    for device_name, config in CONFIGS.items():
        if restore_device(device_name, config):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "="*60)
    print(f"Restoration Complete: {success_count} succeeded, {fail_count} failed")
    print("="*60)

    if fail_count > 0:
        print("[!] Some devices could not be restored. Verify EVE-NG lab is running and try again.")
        sys.exit(1)
    else:
        print("[+] All devices restored to correct configuration!")
        print("[+] Lab is ready for normal operation.")

if __name__ == "__main__":
    main()
