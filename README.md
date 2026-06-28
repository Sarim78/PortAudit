# PortAudit

**Detects peripherals pretending to be something they're not.**

PortAudit is a cross-platform security tool that profiles wired devices when they connect (USB drives, hubs, cables, docks) and flags behavior consistent with malicious peripherals like BadUSB attacks, keystroke injection, and impostor devices.

> **Note:** This is a personal portfolio project built to explore USB-level security, device fingerprinting, and cross-platform tool design. It is a learning-focused project, not a commercial product.

---

## Why this exists

Not every device you plug in is what it claims to be. A BadUSB device looks like an ordinary flash drive but secretly registers as a keyboard so it can type out commands the moment you connect it. Malicious cables hide a tiny computer inside the connector. The host sees these devices through how they describe themselves and how they behave, and that is exactly what PortAudit watches.

## What it does

- **Device fingerprinting.** Reads each device's vendor ID, product ID, serial number, and declared USB classes, then builds a stable fingerprint.
- **BadUSB detection.** Flags the classic attack signature: a device that claims to be storage but also registers as a keyboard, or any storage device that quietly adds an HID interface.
- **Keystroke injection detection.** Watches newly connected keyboards and measures typing cadence. Real humans type at human speed; malicious devices fire keystrokes far faster than any person can.
- **Known-good whitelist.** Keep a registry of the devices you actually own. Anything new, or anything that no longer matches its previous fingerprint, gets flagged for review.

## Honest limitations

PortAudit is a behavioral and descriptor-based tool, not a hardware verifier. You should know what it cannot do:

- It cannot x-ray a cable or read every chip's firmware. It judges devices by how they present to the OS and how they act.
- Pure display devices like plain HDMI extenders expose very little to inspect. The real risk in that category appears when a dock or extender also carries USB, which puts it back inside the USB threat model PortAudit already covers.
- On Windows, talking to some devices directly through libusb may require a driver shim. Where that is not appropriate (you should never rebind the driver on your actual keyboard), PortAudit reads descriptors through the system device registry instead.

These are not gaps to hide. They are the accurate boundary of what software on the host can verify, and naming them is part of the point.

## How it works

PortAudit is built as a pure, OS-agnostic core with platform-specific behavior quarantined behind a single interface.

```
portaudit/
├── core/         device model, enumeration, whitelist, diffing engine
├── platform/     swappable monitor backends behind one interface
└── detectors/    risk checks (BadUSB, keystroke injection)
```

The `core` and `detectors` packages never know which operating system they are running on. All platform differences live behind `platform/base.py`. Today there is one universal backend, `polling.py`, that re-enumerates devices on a short interval and works on every OS. Native event backends (udev on Linux, device-change messages on Windows, IOKit on macOS) can be added next to it without touching anything else.

## Install

Requires Python 3.9+.

```bash
git clone https://github.com/Sarim78/portaudit.git
cd portaudit
pip install -r requirements.txt
```

On Linux, raw USB access may require running with elevated privileges or adding a udev rule for your user.

## Usage

```bash
# List every connected device and its fingerprint
python -m portaudit list

# Run a one-time risk scan and print findings
python -m portaudit scan

# Add the currently connected devices to your trusted whitelist
python -m portaudit trust

# Watch continuously and alert on risky or unknown devices
python -m portaudit watch
```

## Disclaimer

PortAudit is a defensive security tool for inspecting devices on systems you own or are authorized to test. It does not modify or attack connected devices.
