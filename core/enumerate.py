"""Cross-platform USB enumeration via pyusb/libusb.

pyusb is imported lazily so the CLI can show a clean, friendly error instead of
a traceback if the backend is missing on the user's machine.
"""

from __future__ import annotations

from typing import List, Optional

from .device import Device, Interface

try:
    import usb.core
    import usb.util

    _USB_IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - depends on host environment
    usb = None  # type: ignore
    _USB_IMPORT_ERROR = str(exc)


class EnumerationError(RuntimeError):
    pass


def _safe_string(dev, index) -> str:
    """Reading string descriptors can fail on permissions; never crash on it."""
    try:
        if index:
            return usb.util.get_string(dev, index) or ""
    except Exception:
        pass
    return ""


def enumerate_devices() -> List[Device]:
    """Return every USB device currently visible to the host."""
    if usb is None:
        raise EnumerationError(
            "pyusb is not available: "
            + (_USB_IMPORT_ERROR or "unknown import error")
            + "\nInstall it with:  pip install pyusb"
        )

    try:
        raw_devices = list(usb.core.find(find_all=True))
    except usb.core.NoBackendError:
        raise EnumerationError(
            "No USB backend found. PortAudit needs libusb.\n"
            "  - Linux:   sudo apt install libusb-1.0-0\n"
            "  - macOS:   brew install libusb\n"
            "  - Windows: install a libusb driver via Zadig, or run as admin"
        )
    except Exception as exc:
        raise EnumerationError(f"Failed to enumerate USB devices: {exc}")

    devices: List[Device] = []
    for dev in raw_devices:
        interfaces: List[Interface] = []
        try:
            for cfg in dev:
                for intf in cfg:
                    interfaces.append(
                        Interface(
                            cls=int(intf.bInterfaceClass),
                            subclass=int(intf.bInterfaceSubClass),
                            protocol=int(intf.bInterfaceProtocol),
                        )
                    )
        except Exception:
            # Some devices won't expose their config without a claim; keep the
            # device but skip the interface detail rather than dropping it.
            pass

        devices.append(
            Device(
                vendor_id=int(dev.idVendor),
                product_id=int(dev.idProduct),
                device_class=int(dev.bDeviceClass),
                serial=_safe_string(dev, dev.iSerialNumber),
                manufacturer=_safe_string(dev, dev.iManufacturer),
                product=_safe_string(dev, dev.iProduct),
                interfaces=interfaces,
            )
        )
    return devices
