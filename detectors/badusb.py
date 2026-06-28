"""BadUSB detector.

The core tell: a device that carries storage but ALSO presents a keyboard
(or any HID input) interface. Real flash drives are mass storage only; a
rubber-ducky style implant adds an HID keyboard so it can inject keystrokes.
"""

from __future__ import annotations

from typing import List

from ..core.constants import CLASS_HUB, class_name
from ..core.device import Device
from ..core.finding import Finding
from .base import Detector


class BadUsbDetector(Detector):
    name = "badusb"

    def check(self, device: Device) -> List[Finding]:
        findings: List[Finding] = []

        if device.has_storage and device.has_keyboard:
            findings.append(
                Finding(
                    device=device,
                    severity="critical",
                    title="Storage device also acts as a keyboard",
                    detail=(
                        "This device presents both mass-storage and HID "
                        "keyboard interfaces. That is the classic BadUSB "
                        "signature: it can mount as a drive while silently "
                        "injecting keystrokes. Do not trust it."
                    ),
                )
            )
        elif device.has_storage and device.has_hid:
            findings.append(
                Finding(
                    device=device,
                    severity="high",
                    title="Storage device also presents an HID interface",
                    detail=(
                        "A normal storage device should not also register as a "
                        "human-input device. Treat this as suspicious."
                    ),
                )
            )

        # A device whose top-level class disagrees with its interfaces is a
        # softer signal (some legit composite devices do this), so keep it low.
        if (
            device.device_class
            and device.device_class != CLASS_HUB
            and device.interfaces
            and device.device_class not in {i.cls for i in device.interfaces}
        ):
            findings.append(
                Finding(
                    device=device,
                    severity="low",
                    title="Declared device class does not match its interfaces",
                    detail=(
                        f"Top-level class is {class_name(device.device_class)} "
                        f"but interfaces declare "
                        f"{', '.join(class_name(i.cls) for i in device.interfaces)}."
                    ),
                )
            )

        return findings
