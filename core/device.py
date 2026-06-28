"""The core data model: Interface and Device.

A Device is everything PortAudit inspects about one connected peripheral. The
fingerprint is the stable identity used for whitelist matching, and the
behavior probes (has_keyboard, has_storage, ...) are what the detectors read.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List

from .constants import (
    CLASS_HID,
    CLASS_HUB,
    CLASS_MASS_STORAGE,
    HID_PROTOCOL_KEYBOARD,
    HID_PROTOCOL_MOUSE,
    class_name,
)


@dataclass
class Interface:
    """One declared interface on a device."""

    cls: int
    subclass: int
    protocol: int

    @property
    def is_keyboard(self) -> bool:
        return self.cls == CLASS_HID and self.protocol == HID_PROTOCOL_KEYBOARD

    @property
    def is_hid(self) -> bool:
        return self.cls == CLASS_HID

    @property
    def is_storage(self) -> bool:
        return self.cls == CLASS_MASS_STORAGE

    def describe(self) -> str:
        label = class_name(self.cls)
        if self.is_keyboard:
            label += " (keyboard)"
        elif self.cls == CLASS_HID and self.protocol == HID_PROTOCOL_MOUSE:
            label += " (mouse)"
        return label


@dataclass
class Device:
    """A connected USB device and everything we inspect about it."""

    vendor_id: int
    product_id: int
    device_class: int
    serial: str = ""
    manufacturer: str = ""
    product: str = ""
    interfaces: List[Interface] = field(default_factory=list)

    # -- identity ----------------------------------------------------------
    @property
    def vid_pid(self) -> str:
        return f"{self.vendor_id:04X}:{self.product_id:04X}"

    @property
    def fingerprint(self) -> str:
        """Stable identity used for whitelist matching.

        Combines VID:PID, serial, and the sorted set of declared interface
        classes. If a device later changes the interfaces it declares (e.g. a
        flash drive that suddenly also presents a keyboard), the fingerprint
        changes and the whitelist match fails -- which is exactly the point.
        """
        iface_sig = ",".join(
            sorted(f"{i.cls:02X}.{i.protocol:02X}" for i in self.interfaces)
        )
        return f"{self.vid_pid}|{self.serial}|{iface_sig}"

    # -- behavior probes ---------------------------------------------------
    @property
    def has_keyboard(self) -> bool:
        return any(i.is_keyboard for i in self.interfaces)

    @property
    def has_hid(self) -> bool:
        return any(i.is_hid for i in self.interfaces) or self.device_class == CLASS_HID

    @property
    def has_storage(self) -> bool:
        return (
            any(i.is_storage for i in self.interfaces)
            or self.device_class == CLASS_MASS_STORAGE
        )

    @property
    def is_hub(self) -> bool:
        return self.device_class == CLASS_HUB or any(
            i.cls == CLASS_HUB for i in self.interfaces
        )

    def label(self) -> str:
        name = (self.product or self.manufacturer or "").strip()
        return f"{name} [{self.vid_pid}]" if name else f"Device [{self.vid_pid}]"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["fingerprint"] = self.fingerprint
        return d
