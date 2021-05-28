from functools import total_ordering
from nesim.devices.multiple_port_device import MultiplePortDevice
from nesim.frame import Frame
from nesim.ip import IP

@total_ordering
class Route():

    def __init__(self, destination_ip: IP, mask: IP, gateway: IP,
                 interface: int) -> None:
        self.destination_ip = destination_ip
        self.mask = mask
        self.gateway = gateway
        self.interface = interface

    def enroute(self, ip: IP) -> bool:
        masked_ip = ip.raw_value & self.mask.raw_value
        if masked_ip == self.destination_ip:
            return True
        return False

    def __lt__(self, other: object) -> bool:
        return self.mask.raw_value > other.mask.raw_value

    def __eq__(self, other: object) -> bool:
        return self.mask.raw_value == other.mask.raw_value

    def __str__(self) -> str:
        return f'{self.destination_ip} {self.mask} {self.gateway} {self.interface}'

class Router(MultiplePortDevice):
    """Representa un router en la simulación."""

    def on_frame_received(self, frame: Frame, port: str) -> None:
        raise NotImplementedError()
