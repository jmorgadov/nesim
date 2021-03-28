from nesim.devices.cable import DuplexCableHead
from nesim.devices.device import Device


class Switch(Device):

    def __init__(self, name: str, ports_count: int):
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        return super().connect(cable_head, port_name)
        