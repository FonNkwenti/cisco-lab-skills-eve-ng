#!/usr/bin/env python3
"""
verify_ios_commands.py — Test IOS commands against live GNS3 routers.

Connects to verification routers via Netmiko, tests each command in its
correct IOS context, and updates .agent/skills/reference-data/ios-compatibility.yaml
with pass/fail results.

Usage:
    python3 .agent/skills/scripts/verify_ios_commands.py              # test all unknown entries
    python3 .agent/skills/scripts/verify_ios_commands.py cmds.yaml   # test specific list

Prerequisites:
    - GNS3 running with R1 (c7200, port 5001) and R2 (c3725, port 5002) started
    - pip install netmiko pyyaml
"""

import sys
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
        "enter": ["router eigrp ENARSI"],
        "exit": ["no router eigrp ENARSI"],
    },
    "af-ipv4-unicast": {
        "enter": ["router eigrp ENARSI", "address-family ipv4 unicast autonomous-system 100"],
        "exit": ["no router eigrp ENARSI"],
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
    # NM-16ESW switch port (c3725 slot 1). c7200 has no switch ports so
    # context entry will fail on c7200 — all commands auto-fail there.
    "interface-switch": {
        "enter": ["interface FastEthernet1/0"],
        "exit": ["interface FastEthernet1/0", "no switchport"],
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


def has_error(output):
    return any(indicator in output for indicator in ERROR_INDICATORS)


def make_device(port):
    return {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
    }


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


def run_platform_tests(platform_key, port, entries):
    """
    Connect to one platform and test all entries.
    Returns dict: command_string → 'pass' | 'fail'.
    On connection failure, returns empty dict (entries stay unknown).
    """
    print(f"\n[{platform_key}] Connecting on port {port}...")
    results = {}
    try:
        with ConnectHandler(**make_device(port)) as conn:
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


def main():
    data = load_yaml(YAML_PATH)
    all_commands = data["commands"]
    platforms = data["platforms"]

    # If input file provided: add any new entries; mark existing entries for re-test
    if len(sys.argv) > 1:
        extra = load_yaml(sys.argv[1])
        existing_cmds = {e["command"] for e in all_commands}
        for entry in extra["commands"]:
            if entry["command"] not in existing_cmds:
                all_commands.append({
                    "command": entry["command"],
                    "context": entry["context"],
                    "c7200": "unknown",
                    "c3725": "unknown",
                    "notes": entry.get("notes", ""),
                })
                print(f"[+] New entry: {entry['command']!r}")
            else:
                # Reset to unknown so they get re-tested
                for e in all_commands:
                    if e["command"] == entry["command"]:
                        e["c7200"] = "unknown"
                        e["c3725"] = "unknown"
                        break

    # Gather unknown entries per platform
    unknown_c7200 = [e for e in all_commands if e.get("c7200") == "unknown"]
    unknown_c3725 = [e for e in all_commands if e.get("c3725") == "unknown"]

    if not unknown_c7200 and not unknown_c3725:
        print("Nothing to test — no 'unknown' entries in the compatibility record.")
        _print_report(all_commands)
        return

    # Run tests
    if unknown_c7200 and not platforms["c7200"].get("deprecated"):
        results = run_platform_tests("c7200", platforms["c7200"]["console_port"], unknown_c7200)
        for entry in all_commands:
            if entry["command"] in results:
                entry["c7200"] = results[entry["command"]]

    if unknown_c3725:
        results = run_platform_tests("c3725", platforms["c3725"]["console_port"], unknown_c3725)
        for entry in all_commands:
            if entry["command"] in results:
                entry["c3725"] = results[entry["command"]]

    # Write updated YAML
    YAML_PATH.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    )
    print(f"\n[*] {YAML_PATH} updated.")

    _print_report(all_commands)


def _print_report(commands):
    print("\n=== IOS Compatibility Report ===")
    print(f"{'Command':<50} {'Context':<22} {'c7200':<8} c3725")
    print("-" * 100)
    for e in commands:
        c7 = e.get("c7200", "?")
        c3 = e.get("c3725", "?")
        print(f"{e['command']:<50} {e['context']:<22} {c7:<8} {c3}")


if __name__ == "__main__":
    main()
