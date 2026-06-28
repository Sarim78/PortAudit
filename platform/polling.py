"""Universal polling backend.

Re-enumerates devices on an interval and diffs against the last snapshot. Works
on every OS with no native event hooks. Less elegant than real events, but it
ships everywhere day one.
"""

from __future__ import annotations

import time
from typing import Dict

from ..core.device import Device
from ..core.enumerate import enumerate_devices
from .base import Monitor, OnNewDevice


class PollingMonitor(Monitor):
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self._seen: Dict[str, Device] = {}

    @staticmethod
    def _key(device: Device) -> str:
        return device.fingerprint

    def poll_once(self) -> list:
        """Return devices that are newly present since the last poll."""
        current = {self._key(d): d for d in enumerate_devices()}
        new = [d for k, d in current.items() if k not in self._seen]
        self._seen = current
        return new

    def run(self, on_new: OnNewDevice) -> None:
        # Seed the baseline so we only alert on changes after startup.
        self._seen = {self._key(d): d for d in enumerate_devices()}
        try:
            while True:
                time.sleep(self.interval)
                for device in self.poll_once():
                    on_new(device)
        except KeyboardInterrupt:
            print("\nStopped.")
