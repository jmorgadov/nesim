from typing import Dict, List
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.cable import DuplexCableHead
from nesim.devices.device import Device
from nesim.devices.utils import from_bit_data_to_number
from pathlib import Path

class Switch(Device):

    def __init__(self, name: str, ports_count: int, signal_time: int):
        self.signa_time = signal_time
        self._updating = False
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = self.create_send_receiver(i)
        self.ports_buffer = [[] for _ in range(ports_count)]
        self.mac_table: Dict[int, str] = {}
        super().__init__(name, ports)

    def save_log(self, path=''):
        output_folder = Path(path)
        output_folder.mkdir(parents=True, exist_ok=True)        
        output_path = output_folder / Path(f'{self.name}.txt')
        with open(str(output_path), 'w+') as file:
            header = f'| {"Time (ms)": ^10} |'
            for port in self.ports.keys():
                header += f' {port: ^11} |'
            header_len = len(header)
            header += f'\n| {"": ^10} |'
            for port in self.ports.keys():
                header += f' {"Rece . Sent": ^11} |'
            file.write(f'{"-" * header_len}\n')
            file.write(f'{header}\n')
            file.write(f'{"-" * header_len}\n')
            file.write('\n'.join(self.logs))
            file.write(f'\n{"-" * header_len}\n')

    def special_log(self, time: int, received: List[int], sent: List[int]):
        """
        Representación especial para los logs de los switch.

        Parameters
        ----------
        time : int
            Timepo de ejecución de la simulación.
        received : List[int]
            Lista de bits recibidos por cada puerto.        
        sent : List[int]
            Lista de bits enviados por cada puerto.
        """

        log_msg = f'| {time: ^10} |'
        for re, se in zip(received, sent):
            if re == '-':
                log_msg += f' {"---" : ^11} |'
            else:
                log_msg += f' {re :>4} . {se: <4} |'
        self.logs.append(log_msg)

    def broadcast(self, data):
        for port in self.ports.values():
            port.send(data)

    def reset(self):
        pass

    def update(self, time: int):
        for send_receiver in self.ports.values():
            send_receiver.update()
        received = [self.get_port_value(p) for p in self.ports]
        sent = [self.get_port_value(p, False) for p in self.ports]
        self.special_log(time, received, sent)
        super().update(time)

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

    def get_port_value(self, port_name: str, received: bool = True):
        """
        Devuelve el valor del cable conectado a un puerto dado. En caso de no
        tener un cable conectado devuelve ``'-'``.

        Parameters
        ----------
        port_name : str
            Nombre del puerto.
        """

        send_receiver = self.ports[port_name]
        bit = None
        if send_receiver.cable_head is not None:
            if received:
                bit = send_receiver.cable_head.receive_value
            else:
                bit = send_receiver.cable_head.send_value
        return str(bit) if bit is not None else '-'

    def receive_on_port(self, port, bit):
        self.ports_buffer[port].append(bit)
        self.handle_buffer_data(port)

    def create_send_receiver(self, port, cable_head: DuplexCableHead = None):
        sr = SendReceiver(self.signa_time, cable_head)
        sr.on_receive.append(lambda bit : self.receive_on_port(port, bit))
        return sr

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        sr = self.ports[port_name]
        if sr.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        sr.cable_head = cable_head

    def disconnect(self, port_name: str):
        self.ports[port_name].disconnect()
        