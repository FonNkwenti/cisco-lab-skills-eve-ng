"""
lab_utils.py -- scaffolding reference for EVE-NG lab setup helpers.

IMPORTANT: Do NOT use ConnectHandler directly in generated lab scripts.
Use connect_node() from labs/common/tools/eve_ng.py instead. That function
handles EVE-NG-specific quirks:
  - clear_buffer() before enable() to drain stale syslog from persistent
    telnet buffers (critical for CSR1000v which emits more post-save output)
  - check_config_mode() guard before 'end' to prevent DNS lookup hang when
    a device without 'no ip domain lookup' is already in exec mode
  - 'no logging console' suppression so syslog lines don't corrupt future
    Netmiko prompt matching on the shared EVE-NG telnet stream
  - device_type parameter for IOS-XR nodes (skips enable/end entirely)

All generated setup_lab.py / apply_solution.py / inject_*.py scripts
already use connect_node() via: from eve_ng import connect_node
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Locate labs/common/tools/ relative to this file's expected installed location.
# Scaffolding is instantiated at labs/<topic>/common/tools/lab_utils.py,
# so labs/common/tools/ is three levels up then into common/tools.
_TOOLS_DIR = Path(__file__).resolve().parents[3] / "common" / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from eve_ng import connect_node, EveNgError  # noqa: E402


class LabSetup:
    def __init__(self, devices, eve_ng_host="192.168.x.x"):
        self.devices = devices          # List of (name, port, config_path)
        self.eve_ng_host = eve_ng_host  # EVE-NG server IP

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False

            commands = []
            with open(config_file) as f:
                for line in f:
                    if line.strip() and not line.startswith("!"):
                        commands.append(line.strip())

            conn = connect_node(host, port)
            try:
                conn.send_config_set(commands)
                conn.send_command("write memory", read_timeout=10)
                print(f"  Successfully loaded {config_file}")
            finally:
                conn.disconnect()
            return True
        except (EveNgError, Exception) as exc:
            print(f"  Failed to connect or push config: {exc}")
            return False

    def run(self):
        print(f"Starting Lab Setup Automation (EVE-NG: {self.eve_ng_host})...")
        for name, port, config in self.devices:
            print(f"--- Setting up {name} ---")
            self.push_config(self.eve_ng_host, port, config)


class LabRefresher:
    def __init__(self, devices, eve_ng_host="192.168.x.x"):
        self.devices = devices          # List of (name, port, config_path)
        self.eve_ng_host = eve_ng_host  # EVE-NG server IP

    def _parse_cleanup_commands(self, config_file):
        """Parse config to find interfaces and routing protocols to reset."""
        interfaces = []
        routers = []
        with open(config_file) as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("interface "):
                    interfaces.append(stripped.split(" ", 1)[1])
                elif stripped.startswith("router "):
                    routers.append(stripped)
        cleanup = [f"default interface {iface}" for iface in interfaces]
        cleanup += [f"no {router}" for router in routers]
        return cleanup

    def push_config(self, host, port, config_file):
        print(f"Refreshing {host}:{port} with {config_file}...")
        try:
            conn = connect_node(host, port)
            try:
                cleanup = self._parse_cleanup_commands(config_file)
                if cleanup:
                    conn.send_config_set(cleanup)

                commands = []
                with open(config_file) as f:
                    for line in f:
                        if line.strip() and not line.startswith("!"):
                            commands.append(line.strip())

                conn.send_config_set(commands)
                conn.send_command("write memory", read_timeout=10)
                print("  Successfully refreshed.")
            finally:
                conn.disconnect()
            return True
        except (EveNgError, Exception) as exc:
            print(f"  Failed: {exc}")
            return False

    def run(self):
        for name, port, config_path in self.devices:
            self.push_config(self.eve_ng_host, port, config_path)
