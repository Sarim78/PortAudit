"""Risk detectors and the scan helper that runs all of them."""

from __future__ import annotations

from typing import List

from ..core.device import Device
from ..core.finding import Finding
from .base import Detector
from .badusb import BadUsbDetector

# Register all active detectors here. Adding a new check is a one-line append.
DETECTORS: List[Detector] = [BadUsbDetector()]


def scan_device(device: Device) -> List[Finding]:
    findings: List[Finding] = []
    for det in DETECTORS:
        findings.extend(det.check(device))
    return findings


__all__ = ["Detector", "BadUsbDetector", "DETECTORS", "scan_device"]
