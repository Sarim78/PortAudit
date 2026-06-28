"""CLI command implementations and the argument parser."""

from __future__ import annotations

import argparse
import time
from typing import List, Optional

from .core.enumerate import enumerate_devices, EnumerationError
from .core.finding import Finding, SEVERITY_ORDER
from .core.whitelist import Whitelist
from .detectors import scan_device
from .platform import get_monitor
from .report import print_device, print_findings


def cmd_list(args) -> int:
    devices = enumerate_devices()
    wl = Whitelist()
    if not devices:
        print("No USB devices found.")
        return 0
    print(f"Found {len(devices)} device(s):\n")
    for d in devices:
        print_device(d, trusted=wl.is_trusted(d))
        print()
    return 0


def cmd_scan(args) -> int:
    devices = enumerate_devices()
    wl = Whitelist()
    all_findings: List[Finding] = []
    unknown = []

    for d in devices:
        all_findings.extend(scan_device(d))
        if not wl.is_trusted(d):
            unknown.append(d)

    print(f"Scanned {len(devices)} device(s).\n")

    if all_findings:
        print("Risk findings:")
        print_findings(all_findings)
        print()
    else:
        print("No risk signatures detected.\n")

    if unknown:
        print(f"{len(unknown)} device(s) not in your whitelist:")
        for d in unknown:
            print(f"  - {d.label()}")
        print("  Run 'trust' to whitelist the devices you recognize.\n")

    critical = [f for f in all_findings if f.rank() >= SEVERITY_ORDER["high"]]
    return 1 if critical else 0


def cmd_trust(args) -> int:
    devices = enumerate_devices()
    wl = Whitelist()
    added = 0
    for d in devices:
        risky = [f for f in scan_device(d) if f.rank() >= SEVERITY_ORDER["high"]]
        if risky:
            print(f"Skipping (risky): {d.label()}")
            continue
        if wl.add(d):
            print(f"Trusted: {d.label()}")
            added += 1
    if added:
        wl.save()
    print(f"\n{added} device(s) added to {wl.path}")
    return 0


def cmd_watch(args) -> int:
    wl = Whitelist()
    monitor = get_monitor(interval=args.interval)

    def on_new(device) -> None:
        ts = time.strftime("%H:%M:%S")
        print(f"\n[{ts}] Device connected: {device.label()}")
        findings = scan_device(device)
        if findings:
            print_findings(findings)
        if not wl.is_trusted(device):
            print("         (not in whitelist - verify before trusting)")
        elif not findings:
            print("         trusted, no risk signatures.")

    print(f"Watching for new devices (poll every {args.interval}s). Ctrl+C to stop.")
    monitor.run(on_new)
    return 0


COMMANDS = {
    "list": cmd_list,
    "scan": cmd_scan,
    "trust": cmd_trust,
    "watch": cmd_watch,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="portaudit",
        description="Detects peripherals pretending to be something they're not.",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list connected devices and fingerprints")
    sub.add_parser("scan", help="run a one-time risk scan")
    sub.add_parser("trust", help="add current devices to the whitelist")
    w = sub.add_parser("watch", help="continuously watch for new devices")
    w.add_argument(
        "--interval", type=float, default=1.0,
        help="seconds between polls (default: 1.0)",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.command](args)
    except EnumerationError as exc:
        import sys
        print(f"Error: {exc}", file=sys.stderr)
        return 2
