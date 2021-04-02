from typing import List
from pathlib import Path
from nesim.devices.send_receiver import SendReceiver
from nesim.devices.device import Device
from nesim.devices.cable import DuplexCableHead
from nesim.devices.utils import from_bit_data_to_number


class Host(Device):
    """
    Representa una PC (Host).

    Parameters
    ----------
    name : str
        Nombre de la PC.
    signal_time : int
        Tiempo mínimo que debe estar un bit en transmisión.

    Attributes
    ----------
    data : List[int]
        Datos que debe enviar la PC.
    """

    def __init__(self, name: str, signal_time: int):
        self.signal_time = signal_time
        self.mac = None
        self.send_receiver = self.create_send_receiver()
        ports = {f'{name}_1' : self.send_receiver}

        # Data receiving stuff
        self.received_data = []
        self.buffer = []
        self.is_receiving_data = False
        self.frame_start_index = 0
        self.data_size = None
        self.data_from = None

        super().__init__(name, ports)

    @property
    def str_mac(self):
        """str : Dirección mac del host."""
        if self.mac is not None:
            return ''.join(map(str, self.mac))

    @property
    def cable_head(self):
        """DuplexCableHead : Extremo del cable conectado a la PC"""
        return self.ports[self.port_name(1)]

    @property
    def is_connected(self):
        """bool : Estado de conección del host"""
        return self.send_receiver is not None and \
               self.send_receiver.cable_head is not None

    @property
    def is_active(self):
        return self.send_receiver.is_active

    def save_log(self, path: str = ''):
        super().save_log(path=path)

        output_path = Path(path) / Path(f'{self.name}_data.txt')
        with open(output_path, 'w+') as data_file:
            data = [' '.join(map(str, d)) + '\n' for d in self.received_data]
            data_file.writelines(data)

    def update(self, time):
        super().update(time)
        self.send_receiver.update()

    def send(self, data: List[List[int]]):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[List[int]]
            Datos a ser enviados.
        """
        self.send_receiver.send(data)

    def receive(self):
        """
        Lee del cable al que está conectado.

        Si la PC se encuentra enviando infromación entonces comprueba que no
        haya colisión.

        En caso contrario almacena la lectura del cable en varios ocaciones
        entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
        se guarda como lectura final la moda de los datos almacenados.
        """
        self.send_receiver.receive()

    def received_bit(self, bit: int):
        """
        Se ejecuta cada vez que el host recibe un bit. Procesa la información
        en el buffer para indentificar frames cuyo destino sea el host en
        cuestión.

        Parameters
        ----------
        bit : int
            Bit recibido.
        """

        self.log(self.sim_time, 'Received', f'{bit}')
        self.buffer.append(bit)

        if bit is None:
            self.is_receiving_data = False
            self.buffer = []
            self.data_from = None
            self.frame_start_index = 0
            self.data_size = 0
            return

        if self.is_receiving_data:
            received_size = len(self.buffer) - self.frame_start_index
            fsi = self.frame_start_index
            if received_size == 48:
                _from = from_bit_data_to_number(
                    self.buffer[fsi + 16:fsi + 32]
                )
                self.data_from = str(hex(_from))[2:].upper()
                self.data_size = from_bit_data_to_number(
                    self.buffer[fsi + 32:fsi + 40]
                )
            elif received_size > 48 and received_size == 48 + 8*self.data_size:
                data = from_bit_data_to_number(self.buffer[fsi + 48:])
                hex_data = str(hex(data))[2:].upper()
                if len(hex_data) % 4 != 0:
                    rest = 4 - len(hex_data) % 4
                    hex_data = '0'*rest + hex_data
                self.received_data.append(
                    [self.sim_time, self.data_from, hex_data]
                )

        last = self.buffer[-16:]
        if ''.join(map(str, last)) == self.str_mac:
            self.is_receiving_data = True
            self.frame_start_index = len(self.buffer) - 16


    def create_send_receiver(self):
        """Crea un ``SendReceiver``.

        Returns
        -------
        SendReceiver
            ``SendReceiver`` creado.
        """

        send_receiver = SendReceiver(self.signal_time)

        send_receiver.on_send.append(
            lambda bit: self.log(self.sim_time, 'Sent', f'{bit}')
        )

        send_receiver.on_receive.append(
            lambda bit: self.received_bit(bit)
        )

        send_receiver.on_collision.append(
            lambda : self.log(self.sim_time,
                     'Collision',
                     f'Waitting {send_receiver.time_to_send}ms to send')
        )
        return send_receiver

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        if self.send_receiver.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.send_receiver.cable_head = cable_head

        self.log(self.sim_time, 'Connected')

    def disconnect(self, port_name: str):
        self.send_receiver.disconnect()
        self.log(self.sim_time, 'Disconnected')
