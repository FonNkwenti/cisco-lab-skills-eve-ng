#!/usr/bin/env python3
"""
verify_ios_commands.py — Test IOS commands against live EVE-NG routers.

Connects to routers via Netmiko, tests each command in its correct IOS
context, and updates .agent/skills/reference-data/ios-compatibility.yaml
with pass/fail results.

Usage:
    # Test all unknown entries on default platforms (iosv + iosvl2)
    python3 .agent/skills/scripts/verify_ios_commands.py

    # Test specific platforms only
    python3 .agent/skills/scripts/verify_ios_commands.py --platforms iosv iosvl2

    # Test and add new command entries from a file
    python3 .agent/skills/scripts/verify_ios_commands.py cmds.yaml

    # Legacy GNS3 mode (Dynamips via localhost)
    python3 .agent/skills/scripts/verify_ios_commands.py --legacy

Prerequisites:
    - EVE-NG lab running with test routers:
        * iosv_test  — IOSv node (routing tests)
        * iosvl2_test — IOSvL2 node (switching tests)
    - Ports discoverable via EVE-NG REST API, or passed manually via --ports
    - pip install netmiko pyyaml requests

Examples:
    # Discover ports via REST API
    python3 verify_ios_commands.py --host 192.168.1.100 --lab test_lab.unl

    # Specify ports manually (IOSv=32768, IOSvL2=32769)
    python3 verify_ios_commands.py --host 192.168.1.100 --ports iosv=32768 iosvl2=32769
"""

import sys
import argparse
import yaml
from pathlib import Path
from netmiko import ConnectHandler

YAML_PATH = Path(".agent/skills/reference-data/ios-compatibility.yaml")

ERROR_INDICATORS = [
    "% Invalid input detected",
    "% Unrecognized command",
    "% Incomplete command",
]

# Each context: setup commands to enter, cleanup commands to exit
CONTEXT_MAP = {
    "global": {"enter": [], "exit": []},
    "interface": {
        "enter": ["interface Loopback99"],
        "exit": ["no interface Loopback99"],
    },
    "router-eigrp": {
        "enter": ["router eigrp 100"],
        "exit": ["no router eigrp 100"],
    },
    "router-eigrp-named": {
        "enter": ["router eigrp VERIFY_TEST"],
        "exit": ["no router eigrp VERIFY_TEST"],
    },
    "af-ipv4-unicast": {
        "enter": ["router eigrp VERIFY_TEST", "address-family ipv4 unicast autonomous-system 100"],
        "exit": ["no router eigrp VERIFY_TEST"],
    },
    "router-ospf": {
        "enter": ["router ospf 1"],
        "exit": ["no router ospf 1"],
    },
    "router-bgp": {
        "enter": ["router bgp 65000"],
        "exit": ["no router bgp 65000"],
    },
    "af-ipv4-bgp": {
        "enter": ["router bgp 65000", "address-family ipv4"],
        "exit": ["no router bgp 65000"],
    },
    "router-ospfv3": {
        "enter": ["router ospfv3 1"],
        "exit": ["no router ospfv3 1"],
    },
    # IOSvL2: GigabitEthernet1/0 is a switchport (in slot 1).
    # IOSv/CSR1000v have no switchports — context entry fails automatically.
    "interface-switch": {
        "enter": ["interface GigabitEthernet1/0"],
        "exit": ["interface GigabitEthernet1/0", "no switchport"],
    },
}

# Test contexts in dependency order (parent before child)
CONTEXT_ORDER = [
    "global", "interface", "interface-switch",
    "router-eigrp", "router-eigrp-named", "af-ipv4-unicast",
    "router-ospf", "router-ospfv3",
    "router-bgp", "af-ipv4-bgp",
]

# Child context → required parent context (auto-fail if parent fails)
CONTEXT_DEPS = {
    "af-ipv4-unicast": "router-eigrp-named",
    "af-ipv4-bgp": "router-bgp",
}

# Platform → which YAML column to write results to
# Maps each active platform to its group column in ios-compatibility.yaml
PLATFORM_COLUMN_MAP = {
    "iosv":     "ios-classic",
    "iosvl2":   "ios-l2",
    "csr1000v": "ios-xe",
    "iol_l3":   "ios-classic",
    "iol_l2":   "ios-l2",
    # Legacy Dynamips columns (still present in YAML, preserved for history)
    "c7200":    "c7200",
    "c3725":    "c3725",
}


def has_error(output):
    return any(indicator in output for indicator in ERROR_INDICATORS)


def make_device(host, port, use_ssh=False, username="admin", password="eve"):
    """Build Netmiko device dict for EVE-NG console (telnet) or SSH."""
    if use_ssh:
        return {
            "device_type": "cisco_ios",
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "global_delay_factor": 2,
        }
    return {
        "device_type": "cisco_ios_telnet",
        "host": host,
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
    }


def discover_ports_via_api(host, lab_path, username="admin", password="eve"):
    """Query EVE-NG REST API to get node telnet ports. Returns {node_name: port}."""
    try:
        import requests
        session = requests.Session()
        r = session.post(f"http://{host}/api/auth/login",
                         json={"username": username, "password": password})
        r.raise_for_status()
        r2 = session.get(f"http://{host}/api/labs/{lab_path}/nodes")
        r2.raise_for_status()
        nodes = r2.json().get("data", {})
        result = {}
        for node in nodes.values():
            name = node.get("name", "")
            url = node.get("url", "")
            if url and ":" in url:
                try:
                    result[name] = int(url.split(":")[-1])
                except ValueError:
                    pass
        return result
    except Exception as e:
        print(f"[!] REST API port discovery failed: {e}")
        return {}


def safe_cleanup(conn, exit_cmds):
    if exit_cmds:
        try:
            conn.send_config_set(exit_cmds)
        except Exception:
            pass


def test_context_entry(conn, context):
    """Return True if context entry commands succeed on this platform."""
    ctx = CONTEXT_MAP[context]
    if not ctx["enter"]:
        return True
    output = conn.send_config_set(ctx["enter"])
    safe_cleanup(conn, ctx["exit"])
    return not has_error(output)


def test_command(conn, context, command):
    """Send command in its context. Return 'pass' or 'fail'."""
    ctx = CONTEXT_MAP[context]
    output = conn.send_config_set(ctx["enter"] + [command])
    safe_cleanup(conn, ctx["exit"])
    return "fail" if has_error(output) else "pass"


def run_platform_tests(platform_key, host, port, entries, use_ssh=False):
    """
    Connect to one platform and test all entries.
    Returns dict: command_string → 'pass' | 'fail'.
    On connection failure, returns empty dict (entries stay unknown).
    """
    col = PLATFORM_COLUMN_MAP.get(platform_key, platform_key)
    print(f"\n[{platform_key} → column:{col}] Connecting to {host}:{port}...")
    results = {}
    try:
        with ConnectHandler(**make_device(host, port, use_ssh)) as conn:
            conn.enable()
            print(f"[{platform_key}] Connected.")

            # Pre-check each needed context in dependency order
            needed_contexts = {e["context"] for e in entries}
            context_ok = {}
            for ctx in CONTEXT_ORDER:
                if ctx not in needed_contexts:
                    continue
                dep = CONTEXT_DEPS.get(ctx)
                if dep and not context_ok.get(dep, True):
                    context_ok[ctx] = False
                    print(f"  [{platform_key}] Context '{ctx}': auto-fail (parent '{dep}' failed)")
                    continue
                ok = test_context_entry(conn, ctx)
                context_ok[ctx] = ok
                print(f"  [{platform_key}] Context '{ctx}': {'ok' if ok else 'FAIL'}")

            # Test each command
            for entry in entries:
                ctx = entry["context"]
                cmd = entry["command"]
                if not context_ok.get(ctx, True):
                    results[cmd] = "fail"
                    print(f"  [{platform_key}] [skip] {cmd!r} — context unavailable")
                else:
                    result = test_command(conn, ctx, cmd)
                    results[cmd] = result
                    icon = "+" if result == "pass" else "!"
                    print(f"  [{platform_key}] [{icon}] {cmd!r} → {result}")

    except Exception as exc:
        print(f"[{platform_key}] Connection failed: {exc}")
        print(f"[{platform_key}] Entries remain 'unknown' in YAML.")

    return results


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())


def parse_args():
    parser = argparse.ArgumentParser(description="Verify IOS command compatibility on EVE-NG nodes")
    parser.add_argument("cmds_file", nargs="?", help="Optional YAML file with new commands to test")
    parser.add_argument("--host", default="127.0.0.1",
                        help="EVE-NG host IP (default: 127.0.0.1 for legacy GNS3 mode)")
    parser.add_argument("--lab", help="EVE-NG lab path (e.g. 'verify_lab.unl') for API port discovery")
    parser.add_argument("--ports", nargs="*",
                        help="Manual port overrides: iosv=32768 iosvl2=32769")
    parser.add_argument("--platforms", nargs="*",
                        default=["iosv", "iosvl2"],
                        help="Platforms to test (default: iosv iosvl2)")
    parser.add_argument("--ssh", action="store_true",
                        help="Use SSH instead of telnet for connections")
    parser.add_argument("--legacy", action="store_true",
                        help="Legacy GNS3 mode: use 127.0.0.1 with c7200 (port 5001) and c3725 (port 5002)")
    return parser.parse_args()


def main():
    args = parse_args()
    data = load_yaml(YAML_PATH)
    all_commands = data["commands"]
    platforms_yaml = data["platforms"]

    # Legacy GNS3 mode
    if args.legacy:
        print("[legacy] GNS3 mode: testing c7200 (5001) and c3725 (5002) on localhost")
        args.host = "127.0.0.1"
        args.platforms = ["c7200", "c3725"]
        port_map = {"c7200": 5001, "c3725": 5002}
    else:
        port_map = {}

    # Parse manual port overrides
    if args.ports:
        for pair in args.ports:
            k, v = pair.split("=")
            port_map[k.strip()] = int(v.strip())

    # Discover ports via REST API if lab specified
    if args.lab and not args.legacy:
        discovered = discover_ports_via_api(args.host, args.lab)
        if discovered:
            print(f"[API] Discovered ports: {discovered}")
            port_map.update(discovered)

    # If input file provided: add any new entries or reset existing for re-test
    if args.cmds_file:
        extra = load_yaml(args.cmds_file)
        existing_cmds = {e["command"] for e in all_commands}
        for entry in extra["commands"]:
            if entry["command"] not in existing_cmds:
                new_entry = {
                    "command": entry["command"],
                    "context": entry["context"],
                    "ios-classic": "unknown",
                    "ios-l2": "unknown",
                    "ios-xe": "unknown",
                    "notes": entry.get("notes", ""),
                }
                # Preserve legacy columns if present in YAML
                if any("c7200" in e for e in all_commands):
                    new_entry["c7200"] = "unknown"
                    new_entry["c3725"] = "unknown"
                all_commands.append(new_entry)
                print(f"[+] New entry: {entry['command']!r}")
            else:
                for e in all_commands:
                    if e["command"] == entry["command"]:
                        for platform in args.platforms:
                            col = PLATFORM_COLUMN_MAP.get(platform, platform)
                            e[col] = "unknown"
                        break

    # For each active platform: collect unknown entries and test
    for platform in args.platforms:
        if platforms_yaml.get(platform, {}).get("deprecated") and not args.legacy:
            print(f"[skip] {platform} is deprecated — use --legacy to test Dynamips platforms")
            continue

        col = PLATFORM_COLUMN_MAP.get(platform, platform)
        unknown_entries = [e for e in all_commands if e.get(col) == "unknown"]

        if not unknown_entries:
            print(f"[{platform}] Nothing to test — no 'unknown' entries for column '{col}'")
            continue

        port = port_map.get(platform)
        if port is None:
            print(f"[{platform}] No port configured — skipping. Use --ports {platform}=<port> or --lab to discover.")
            continue

        results = run_platform_tests(platform, args.host, port, unknown_entries, use_ssh=args.ssh)
        for entry in all_commands:
            if entry["command"] in results:
                entry[col] = results[entry["command"]]

    # Write updated YAML
    YAML_PATH.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    )
    print(f"\n[*] {YAML_PATH} updated.")

    _print_report(all_commands)


def _print_report(commands):
    print("\n=== IOS Compatibility Report ===")
    print(f"{'Command':<50} {'Context':<22} {'ios-classic':<13} {'ios-l2':<10} ios-xe")
    print("-" * 110)
    for e in commands:
        ic  = e.get("ios-classic", "?")
        il2 = e.get("ios-l2", "?")
        xe  = e.get("ios-xe", "?")
        print(f"{e['command']:<50} {e['context']:<22} {ic:<13} {il2:<10} {xe}")


if __name__ == "__main__":
    main()
