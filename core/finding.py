"""Finding: a single risk result produced by a detector."""

from __future__ import annotations

from dataclasses import dataclass

from .device import Device

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass
class Finding:
    device: Device
    severity: str
    title: str
    detail: str

    def rank(self) -> int:
        return SEVERITY_ORDER.get(self.severity, 0)
