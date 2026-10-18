#!/usr/bin/env python3
# =============================================================================
# find_pi.py — listen for astro-beacon broadcasts and print every Pi found.
# Run on your laptop (Linux / macOS / Windows), same network as the Pi:
#     python3 find_pi.py            # listen 15 s, then print summary
#     python3 find_pi.py -t 0       # listen forever
# Standard library only.
# =============================================================================

import argparse
import json
import socket
import time

MAGIC = "rpi5_astro"


def main():
    ap = argparse.ArgumentParser(description="Find rpi5_astro beacons on the LAN")
    ap.add_argument("-p", "--port", type=int, default=50505)
    ap.add_argument("-t", "--timeout", type=float, default=15,
                    help="seconds to listen (0 = forever)")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", args.port))
    sock.settimeout(1)

    print(f"Listening for beacons on UDP {args.port} ...")
    seen = {}
    deadline = time.time() + args.timeout if args.timeout else None
    while deadline is None or time.time() < deadline:
        try:
            data, (src, _) = sock.recvfrom(4096)
        except socket.timeout:
            continue
        try:
            msg = json.loads(data)
        except ValueError:
            continue
        if msg.get("magic") != MAGIC:
            continue

        key = msg.get("hostname", src)
        if key not in seen:
            ips = ", ".join(f"{k}={v}" for k, v in msg.get("ips", {}).items())
            up = msg.get("uptime", 0)
            power = msg.get("throttled")
            warn = "" if power in (None, "0x0") else "  <-- power issue!"
            print(f"  {key:<16} from {src:<15} [{ips}]  "
                  f"up {up // 3600}h{up % 3600 // 60:02d}m  "
                  f"throttled={power}{warn}")
            print(f"      ssh {src}")
        seen[key] = src

    if not seen:
        print("No beacon heard. Check: same network/subnet? firewall allows UDP "
              f"{args.port} inbound? beacon running (systemctl status astro-beacon)?")


if __name__ == "__main__":
    main()
