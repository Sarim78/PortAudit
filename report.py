"""Console presentation helpers, kept separate from the CLI command logic."""

from __future__ import annotations

from typing import List, Optional

from .core.constants import class_name
from .core.device import Device
from .core.finding import Finding

SEV_TAG = {
    "info": "[ INFO ]",
    "low": "[ LOW  ]",
    "medium": "[ MED  ]",
    "high": "[ HIGH ]",
    "critical": "[ CRIT ]",
}


def print_device(device: Device, trusted: Optional[bool] = None) -> None:
    tag = ""
    if trusted is True:
        tag = "  (trusted)"
    elif trusted is False:
        tag = "  (UNKNOWN)"
    print(f"- {device.label()}{tag}")
    print(f"    class:      {class_name(device.device_class)}")
    if device.serial:
        print(f"    serial:     {device.serial}")
    if device.interfaces:
        ifaces = ", ".join(i.describe() for i in device.interfaces)
        print(f"    interfaces: {ifaces}")
    print(f"    fingerprint:{device.fingerprint}")


def print_findings(findings: List[Finding]) -> None:
    for f in sorted(findings, key=lambda x: -x.rank()):
        print(f"{SEV_TAG.get(f.severity, '[ ???? ]')} {f.device.label()}")
        print(f"         {f.title}")
        print(f"         {f.detail}")
