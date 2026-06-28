"""USB class codes and lookup helpers.

A USB device declares what it is through class codes (bDeviceClass and, per
interface, bInterfaceClass). We care most about HID and Mass Storage, because
the BadUSB attack is a storage device that also speaks HID keyboard.

Reference: https://www.usb.org/defined-class-codes
"""

from __future__ import annotations

from typing import Dict

USB_CLASS_NAMES: Dict[int, str] = {
    0x00: "Per-interface",
    0x01: "Audio",
    0x02: "Communications",
    0x03: "HID",
    0x05: "Physical",
    0x06: "Image",
    0x07: "Printer",
    0x08: "Mass Storage",
    0x09: "Hub",
    0x0A: "CDC-Data",
    0x0B: "Smart Card",
    0x0D: "Content Security",
    0x0E: "Video",
    0x0F: "Personal Healthcare",
    0x10: "Audio/Video",
    0xDC: "Diagnostic",
    0xE0: "Wireless Controller",
    0xEF: "Miscellaneous",
    0xFE: "Application Specific",
    0xFF: "Vendor Specific",
}

CLASS_HID = 0x03
CLASS_MASS_STORAGE = 0x08
CLASS_HUB = 0x09

# HID protocol codes (bInterfaceProtocol when bInterfaceClass == HID).
HID_PROTOCOL_KEYBOARD = 0x01
HID_PROTOCOL_MOUSE = 0x02


def class_name(code: int) -> str:
    return USB_CLASS_NAMES.get(code, f"Unknown(0x{code:02X})")
