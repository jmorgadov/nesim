from nesim.devices.send_receiver import SendReceiver
from nesim.devices.cable import DuplexCableHead
from nesim.devices.device import Device


class Switch(Device):

    def __init__(self, name: str, ports_count: int, signal_time: int):
        self.signa_time = signal_time
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    def _create_send_receiver(self, cable_head: DuplexCableHead):
        sr = SendReceiver(self.signa_time, cable_head)
        return sr

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        sr = self.ports[port_name]
        if sr is not None and sr.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        if sr is None:
            sr = self._create_send_receiver(cable_head)

        self.ports[port_name] = sr

        