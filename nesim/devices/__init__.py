"""
Contiene todo lo relacionado con dispositivos.
"""

from nesim.devices.device import Device
from nesim.devices.host import Host
from nesim.devices.hub import Hub
from nesim.devices.switch import Switch
from nesim.devices.cable import Cable, Duplex

__all__ = [
    'Device',
    'Host',
    'Hub',
    'Switch',
    'Cable',
    'Duplex'
]
