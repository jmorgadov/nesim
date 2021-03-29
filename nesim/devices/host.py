from nesim.devices.send_receiver import SendReceiver
from nesim.devices.device import Device
from nesim.devices.cable import DuplexCableHead
from random import randint
from collections import Counter
from typing import List

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
        self.send_receiver = self.create_send_receiver()
        ports = {f'{name}_1' : self.send_receiver}
        super().__init__(name, ports)

    @property
    def cable_head(self):
        """DuplexCableHead : Extremo del cable conectado a la PC"""
        return self.ports[self.port_name(1)]

    @property
    def is_connected(self):
        """bool : Estado de conección del host"""
        return self.send_receiver is not None and self.send_receiver.cable_head is not None

    @property
    def is_active(self):
        return self.send_receiver.is_sending or \
               self.send_receiver.time_to_send

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

    def create_send_receiver(self):
        send_receiver = SendReceiver(self.signal_time)

        send_receiver.on_send.append(
            lambda bit: self.log(self.sim_time, 'Sent', f'{bit}')
        )

        send_receiver.on_receive.append(
            lambda bit: self.log(self.sim_time, 'Received', f'{bit}')
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