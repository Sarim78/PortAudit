"""The platform seam.

Monitor is the one interface that platform-specific backends implement. Today
there is a single universal PollingMonitor. Native event backends (udev on
Linux, WM_DEVICECHANGE on Windows, IOKit on macOS) can be added next to it
without the core or detectors knowing which one is running.
"""

from __future__ import annotations

from typing import Callable

from ..core.device import Device

# A callback invoked with each newly-connected device.
OnNewDevice = Callable[[Device], None]


class Monitor:
    def run(self, on_new: OnNewDevice) -> None:
        raise NotImplementedError
