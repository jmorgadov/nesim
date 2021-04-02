from nesim.devices.device import Device
from nesim.devices.cable import DuplexCableHead
from functools import reduce
from typing import List
from pathlib import Path

class Hub(Device):
    """
    Representa un Hub en la simulación.

    Parameters
    ----------
    name : str
        Nombre del hub.
    ports_count : int
        Cantidad de puertos del hub.
    """

    def __init__(self, name: str, ports_count: int):
        self._updating = False
        self._received, self._sent = [], []
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = None

        super().__init__(name, ports)

    @property
    def is_active(self):
        return False

    def reset(self):
        self._updating = False
        for _, cable_head in self.ports.items():
            if cable_head is not None:
                cable_head.send(None)

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
        Representación especial para los logs de los hubs.

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
        if self._updating:
            self.logs[-1] = log_msg
        else:
            self.logs.append(log_msg)

    def get_port_value(self, port_name: str):
        """
        Devuelve el valor del cable conectado a un puerto dado. En caso de no
        tener un cable conectado devuelve ``'-'``.

        Parameters
        ----------
        port_name : str
            Nombre del puerto.
        """
        cable_head = self.ports[port_name]
        bit = None
        if cable_head is not None:
            bit = cable_head.receive()

        return str(bit) if bit is not None else '-'

    def update(self, time):
        super().update(time)
        p_data = [c.receive_cable.value for c in self.ports.values() if c is not None]
        p_data_filt = [bit for bit in p_data if bit is not None]

        val = None
        if p_data_filt:
            val = reduce(lambda x, y: x|y, p_data_filt)

        if not self._updating:
            self._received = [self.get_port_value(p) for p in self.ports.keys()]        

        for _, cable_head in self.ports.items():
            if cable_head is not None:
                cable_head.send(val)
                if cable_head.receive_value is not None:
                    cable_head.receive_cable.value = val

        self._sent = [self.get_port_value(p) for p in self.ports.keys()]
        self.special_log(time, self._received, self._sent)
        self._updating = True

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        if self.ports[port_name] is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[port_name] = cable_head

    def disconnect(self, port_name: str):
        return super().disconnect(port_name)