"""Platform backends. get_monitor() returns the right one for this host.

For now every OS uses the polling backend. When native backends are added,
this is the single place that decides which to use.
"""

from __future__ import annotations

from .base import Monitor, OnNewDevice
from .polling import PollingMonitor


def get_monitor(interval: float = 1.0) -> Monitor:
    # Future: detect platform and return udev/Windows/IOKit backend if present.
    return PollingMonitor(interval=interval)


__all__ = ["Monitor", "OnNewDevice", "PollingMonitor", "get_monitor"]
