import abc
from nesim.frame import Frame
from typing import Dict, List
from pathlib import Path
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.cable import DuplexCableHead
from nesim.devices.device import Device


class MultiplePortDevice(Device, metaclass=abc.ABCMeta):
    """Representa un dispositivo que contiene múltiples puertos.

    Parameters
    ----------
    name : str
        Nombre del dispositivo
    ports_count : int
        Cantidad de puertos
    signal_time : int
        ``Signal time`` de la simulación
    """

    def __init__(self, name: str, ports_count: int, signal_time: int):
        self.signa_time = signal_time
        self._updating = False
        ports = {}
        for i in range(ports_count):
            ports[f'{name}_{i+1}'] = self.create_send_receiver(i)
        self.ports_buffer = [[] for _ in range(ports_count)]
        self.mac_table: Dict[int, str] = {}
        super().__init__(name, ports)

    @property
    def is_active(self):
        """bool : Estado del switch"""
        return any([sr.is_active for sr in self.ports.values()])

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
        for bit_re, bit_se in zip(received, sent):
            if bit_re == '-'  and bit_se == '-':
                log_msg += f' {"---" : ^11} |'
            else:
                log_msg += f' {bit_re :>4} . {bit_se: <4} |'
        self.logs.append(log_msg)

    def broadcast(self, from_port, data):
        """Envia un frame por todos los puertos.

        Parameters
        ----------
        from_port : str
            Puerto del cual se transmite la información.
        data : List[List[int]]
            Frame a ser enviado.
        """

        for port, send_receiver in self.ports.items():
            if port != from_port and send_receiver.cable_head is not None:
                send_receiver.send(data)

    def reset(self):
        pass

    def update(self, time: int)-> None:
        for send_receiver in self.ports.values():
            send_receiver.update()
        super().update(time)

    def receive(self) -> None:
        """
        Ordena a todos los puertos a recibir la información que les
        esté llegnado. (Leer del cable)
        """

        for send_receiver in self.ports.values():
            if send_receiver.cable_head is not None:
                send_receiver.receive()

        received = [self.get_port_value(p) for p in self.ports]
        sent = [self.get_port_value(p, False) for p in self.ports]
        self.special_log(self.sim_time, received, sent)

    @abc.abstractmethod
    def on_frame_received(self, frame: Frame, port: str) -> None:
        """Este método se ejecuta cada vez que se recibe un frame en
        uno de los puertos.

        Parameters
        ----------
        frame : Frame
            Frame recibido.
        port : str
            Puerto por el cual llegó el frame.
        """

    def handle_buffer_data(self, port: str) -> None:
        """Se encarga de procesar los datos en el buffer de un puerto.

        Parameters
        ----------
        port : str
            Nombre del puerto
        """
        data = self.ports_buffer[port]

        frame = Frame(data)
        if not frame.is_valid:
            return

        self.on_frame_received(frame, port + 1)
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

    def receive_on_port(self, port: str, bit: int):
        """Guarda el bit recibido en un puerto y procesa los datos del mismo.

        Parameters
        ----------
        port : str
            Nombre del puerto.
        bit : int
            Bit recibido
        """

        self.ports_buffer[port].append(bit)
        self.handle_buffer_data(port)

    def create_send_receiver(self, port: str):
        """Crea un ``SendReceiver``.

        Parameters
        ----------
        port : str
            Puerto al que será asignado el ``SendReceiver``.

        Returns
        -------
        SendReceiver
            ``SendReceiver`` creado.
        """

        send_receiver = SendReceiver(self.signa_time, None)
        send_receiver.on_receive.append(
            lambda bit : self.receive_on_port(port, bit)
        )
        return send_receiver

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        send_receiver = self.ports[port_name]
        if send_receiver.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        send_receiver.cable_head = cable_head

    def disconnect(self, port_name: str):
        self.ports_buffer[list(self.ports.keys()).index(port_name)] = []
        self.ports[port_name].disconnect()
