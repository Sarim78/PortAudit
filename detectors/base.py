"""Detector base class. A detector inspects one device and returns findings."""

from __future__ import annotations

from typing import List

from ..core.device import Device
from ..core.finding import Finding


class Detector:
    name = "detector"

    def check(self, device: Device) -> List[Finding]:
        raise NotImplementedError
