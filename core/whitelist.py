"""Whitelist: the known-good device registry.

Stores fingerprints of devices the user has explicitly trusted. Because the
fingerprint includes the declared interface set, a previously-trusted device
that starts presenting new interfaces will no longer match.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict

from .device import Device

WHITELIST_PATH = Path.home() / ".portaudit" / "whitelist.json"


class Whitelist:
    def __init__(self, path: Path = WHITELIST_PATH):
        self.path = path
        self.entries: Dict[str, dict] = {}
        self.load()

    def load(self) -> None:
        if self.path.exists():
            try:
                self.entries = json.loads(self.path.read_text())
            except Exception:
                self.entries = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.entries, indent=2))

    def is_trusted(self, device: Device) -> bool:
        return device.fingerprint in self.entries

    def add(self, device: Device) -> bool:
        """Returns True if newly added, False if already present."""
        if device.fingerprint in self.entries:
            return False
        self.entries[device.fingerprint] = {
            "label": device.label(),
            "vid_pid": device.vid_pid,
            "serial": device.serial,
            "added": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return True
