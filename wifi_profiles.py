#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from typing import Dict, List


def run_command(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return result.stdout


def list_wifi_profiles() -> List[Dict[str, str]]:
    output = run_command([
        "nmcli",
        "-t",
        "-f",
        "NAME,UUID,TYPE,DEVICE,AUTOCONNECT,STATE",
        "connection",
        "show",
    ])

    profiles: List[Dict[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 6:
            continue
        name, uuid, conn_type, device, autoconnect, state = [p.strip() for p in parts[:6]]
        if conn_type == "802-11-wireless":
            profiles.append(
                {
                    "name": name,
                    "uuid": uuid,
                    "type": conn_type,
                    "device": device,
                    "autoconnect": autoconnect,
                    "state": state,
                }
            )
    return profiles


def get_profile_details(profile_name: str) -> Dict[str, str]:
    output = run_command(["nmcli", "-f", "all", "connection", "show", profile_name])
    details: Dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        details[key.strip()] = value.strip()
    return details


def print_profile(profile: Dict[str, str], details: Dict[str, str]) -> None:
    print("=" * 80)
    print(f"Profile: {profile['name']}")
    print(f"UUID: {profile['uuid']}")
    print(f"Type: {profile['type']}")
    print(f"Device: {profile['device'] or '-'}")
    print(f"Auto-connect: {profile['autoconnect']}")
    print(f"State: {profile['state']}")

    if "802-11-wireless.ssid" in details:
        print(f"SSID: {details['802-11-wireless.ssid']}")
    if "802-11-wireless.mode" in details:
        print(f"Mode: {details['802-11-wireless.mode']}")
    if "802-11-wireless.bssid" in details:
        print(f"BSSID: {details['802-11-wireless.bssid']}")
    if "802-11-wireless-security.key-mgmt" in details:
        print(f"Key management: {details['802-11-wireless-security.key-mgmt']}")
    if "802-11-wireless-security.auth-alg" in details:
        print(f"Auth algorithm: {details['802-11-wireless-security.auth-alg']}")
    if "802-11-wireless-security.proto" in details:
        print(f"Protocol: {details['802-11-wireless-security.proto']}")

    print("Other details:")
    for key in sorted(details):
        if key.startswith("connection.") or key.startswith("ipv") or key.startswith("802-11"):
            print(f"  - {key}: {details[key]}")


def main() -> int:
    try:
        profiles = list_wifi_profiles()
    except FileNotFoundError:
        print("nmcli was not found. Install NetworkManager and try again.", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Unable to read Wi-Fi profiles: {exc}", file=sys.stderr)
        return 1

    if not profiles:
        print("No saved Wi-Fi profiles were found.")
        return 0

    print(f"Found {len(profiles)} saved Wi-Fi profile(s).")
    for profile in profiles:
        details = get_profile_details(profile["name"])
        print_profile(profile, details)

    return 0


if __name__ == "__main__":
    sys.exit(main())

