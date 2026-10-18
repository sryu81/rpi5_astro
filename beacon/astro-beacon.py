#!/usr/bin/env python3
# =============================================================================
# astro-beacon — periodically broadcasts this Pi's identity on the local network
# so it can be found without nmap or router access. Run find_pi.py on a laptop
# in the same network to listen for it.
# Standard library only.
# =============================================================================

import json
import os
import socket
import subprocess
import time

PORT = int(os.environ.get("BEACON_PORT", "50505"))
INTERVAL = float(os.environ.get("BEACON_INTERVAL", "5"))
MAGIC = "rpi5_astro"


def ipv4_interfaces():
    """Return [(ifname, address, broadcast)] for every non-loopback IPv4 address."""
    out = subprocess.run(["ip", "-o", "-4", "addr", "show"],
                         capture_output=True, text=True).stdout
    result = []
    for line in out.splitlines():
        parts = line.split()
        ifname = parts[1]
        if ifname == "lo":
            continue
        addr = parts[3].split("/")[0]
        brd = parts[parts.index("brd") + 1] if "brd" in parts else None
        result.append((ifname, addr, brd))
    return result


def throttled():
    """Raspberry Pi undervoltage/throttle flags (0x0 = healthy power)."""
    try:
        out = subprocess.run(["vcgencmd", "get_throttled"],
                             capture_output=True, text=True, timeout=2).stdout
        return out.strip().split("=")[-1]
    except (OSError, subprocess.SubprocessError):
        return None


def uptime_seconds():
    with open("/proc/uptime") as f:
        return int(float(f.read().split()[0]))


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    hostname = socket.gethostname()

    while True:
        ifaces = ipv4_interfaces()
        payload = json.dumps({
            "magic": MAGIC,
            "hostname": hostname,
            "ips": {name: addr for name, addr, _ in ifaces},
            "uptime": uptime_seconds(),
            "throttled": throttled(),
        }).encode()

        # Directed broadcast per interface (works with wlan0 + eth0 + hotspot),
        # plus limited broadcast as a fallback.
        targets = {brd for _, _, brd in ifaces if brd} | {"255.255.255.255"}
        for target in targets:
            try:
                sock.sendto(payload, (target, PORT))
            except OSError:
                pass  # interface down / no route yet — retry next cycle

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
