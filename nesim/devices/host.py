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
        ports = {f'{name}_1' : None}
        super().__init__(name, ports)
        self.signal_time = signal_time
        self.data = []
        self.current_package = []
        self.package_index = 0
        self.time_to_send = 0
        self.max_time_to_send = 1
        self.send_time = 0
        self.sending_bit = 0
        self.is_sending = False
        self.time_connected = 0
        self.recived_bits = []

    def readjust_max_time_to_send(self):
        """
        Ajusta el tiempo máximo que será utilizado en la selección aleatoria
        de cuanto tiempo debe esperar para reintentar un envío.
        """
        self.max_time_to_send *= 2

    @property
    def cable_head(self):
        """DuplexCableHead : Extremo del cable conectado a la PC"""
        return self.ports[self.port_name(1)]
    
    @property
    def is_connected(self):
        """bool : Estado de conección del host"""
        return self.cable_head is not None

    def load_package(self):
        """
        Carga el próximo paquete a enviar si hay datos.
        """
        if not self.current_package:
            if self.data:
                self.current_package = self.data[:8]
                self.data = self.data[8:]
                self.max_time_to_send = 16
                self.package_index = 0
                self.send_time = 0
                self.is_sending = True
            elif self.is_sending:
                self.sending_bit = 0
                self.is_sending = False
                self.cable_head.send(0)


    def update(self, time):
        super().update(time)

        self.load_package()

        if self.time_to_send:
            self.time_to_send -= 1

        if self.time_to_send:
            return
        
        if self.current_package:
            self.is_sending = True
            self.sending_bit = self.current_package[self.package_index]
            # self.log(time, f'Trying to send {self.sending_bit}')
            self.cable_head.send(self.sending_bit)


        self.time_connected += 1

    def send(self, data: List[int]):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[int]
            Datos a ser enviados.
        """
        self.data += data

    def receive(self):
        """
        Lee del cable al que está conectado.

        Si la PC se encuentra enviando infromación entonces comprueba que no
        haya colisión.

        En caso contrario almacena la lectura del cable en varios ocaciones
        entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
        se guarda como lectura final la moda de los datos almacenados.
        """
        if self.is_sending:
            coll = self.check_collision()

            if not coll:                
                if self.send_time == 0:                
                    self.log(self.sim_time, 'Sent', f'{self.sending_bit}')
                self.send_time += 1
                if self.send_time == self.signal_time:
                    self.package_index += 1
                    if self.package_index == len(self.current_package):
                        self.current_package = []              
                    self.send_time = 0

        if self.is_sending:
            return

        elif self.time_connected % self.signal_time//3 == 0:
            self.recived_bits.append(self.cable_head.receive())

        if self.time_connected % self.signal_time == 0 and self.recived_bits:
            temp = [(v,k) for k,v in Counter(self.recived_bits).items()]
            self.log(self.sim_time, 'Received', f'{max(temp)[1]}')
            self.recived_bits = []

    def check_collision(self):
        """
        Comprueba si existe una colisión.

        Returns
        -------
        bool
            ``True`` si hubo colisión, ``False`` en caso contrario.
        """
        if self.is_sending and self.cable_head.receive() != self.sending_bit:
            self.time_to_send = randint(1, self.max_time_to_send)
            self.readjust_max_time_to_send()
            self.log(self.sim_time,
                     'Collision',
                     f'Waitting {self.time_to_send}ms to send')
            self.package_index = 0
            self.send_time = 0
            self.is_sending = False
            return True
        return False

    def connect(self, cable_head: DuplexCableHead, port_name: str):
        if self.cable_head is not None:
            raise ValueError(f'Port {port_name} is currently in use.')

        self.ports[self.port_name(1)] = cable_head
        self.log(self.sim_time, 'Connected')

    def disconnect(self, port_name: str):
        self.data = self.current_package + self.data
        self.current_package = []
        self.package_index = 0
        self.is_sending = False
        self.send_time = 0
        self.sending_bit = 0
        self.max_time_to_send = 16
        self.time_connected = 0
        self.recived_bits = []
        super().disconnect(port_name)
        self.log(self.sim_time, 'Disconnected')