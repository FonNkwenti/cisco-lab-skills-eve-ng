from netmiko import ConnectHandler
import sys
import time
import os

class LabSetup:
    def __init__(self, devices):
        self.devices = devices  # List of (name, port, config_path)

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False

            conn = ConnectHandler(
                device_type='cisco_ios_telnet',
                host=host,
                port=port,
                timeout=5,
            )

            # Read config lines, skipping blanks and comments
            with open(config_file, 'r') as f:
                commands = [
                    line.strip() for line in f
                    if line.strip() and not line.startswith('!')
                ]

            # Push configuration commands
            conn.send_config_set(commands)

            # Save configuration
            conn.send_command("write memory", read_timeout=10)
            print(f"  Successfully loaded {config_file}")

            conn.disconnect()
            return True
        except Exception as e:
            print(f"  Failed to connect or push config: {e}")
            return False

    def run(self):
        print("Starting Lab Setup Automation...")
        for name, port, config in self.devices:
            print(f"--- Setting up {name} ---")
            self.push_config("127.0.0.1", port, config)
        print("Lab Setup Complete.")

# --- Device Mapping Area ---
# This part will be generated dynamically for each lab
