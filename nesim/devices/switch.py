from typing import Dict
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.cable import DuplexCableHead
from nesim.devices.device import Device
from nesim.devices.utils import from_bit_data_to_number

class Switch(Device):

    def __init__(self, name: str, ports_count: int, signal_time: int):
        self.signa_time = signal_time
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None
        self.ports_buffer = [[] for _ in range(ports_count)]
        self.mac_table: Dict[int, str] = {}
        super().__init__(name, ports)

    def broadcast(self, data):
        for port in self.ports.values():
            port.send(data)

    def handle_buffer_data(self, port):
        data = self.ports_buffer[port]

        if len(data) < 40:
            return

        to_mac = from_bit_data_to_number(data[:16])
        from_mac = from_bit_data_to_number(data[16:32])
        size = from_bit_data_to_number(data[32:40]) * 8

        if len(data) - 40 < size:
            return

        self.mac_table[from_mac] = self.port_name(port)

        if to_mac in self.mac_table:
            self.ports[self.mac_table[to_mac]].send(data)
        else:
            self.broadcast(data)
        self.ports_buffer[port] = []


    def receive_on_port(self, port, bit):
        self.ports_buffer[port].append(bit)
        self.handle_buffer_data(port)

    def _create_send_receiver(self, port, cable_head: DuplexCableHead):
        sr = SendReceiver(self.signa_time, cable_head)
        sr.on_receive.append(lambda bit : self.receive_on_port(port, bit))
        return sr

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        sr = self.ports[port_name]
        if sr is not None and sr.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        if sr is None:
            port_num = list(self.ports.keys()).index(port_name)
            sr = self._create_send_receiver(port_num, cable_head)

        self.ports[port_name] = sr

        