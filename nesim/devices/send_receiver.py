from random import randint
from typing import List
from collections import Counter
from nesim.devices.cable import DuplexCableHead

_PACKAGE_SIZE = 8

class SendReceiver():
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

    def __init__(self, signal_time: int, cable_head: DuplexCableHead):
        self.cable_head = cable_head
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
        self.on_send, self.on_receive, self.on_collision = [], [], []

    def readjust_max_time_to_send(self):
        """
        Ajusta el tiempo máximo que será utilizado en la selección aleatoria
        de cuanto tiempo debe esperar para reintentar un envío.
        """
        self.max_time_to_send *= 2

    def load_package(self):
        """
        Carga el próximo paquete a enviar si hay datos.
        """
        if not self.current_package:
            if self.data:
                self.current_package = self.data.pop(0)
                self.max_time_to_send = 16
                self.package_index = 0
                self.send_time = 0
                self.is_sending = True
            elif self.is_sending:
                self.sending_bit = 0
                self.is_sending = False
                self.cable_head.send(None)

    def update(self):
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
        packages = []
        while data:
            packages.append(data[:_PACKAGE_SIZE])
            data = data[_PACKAGE_SIZE:]
        self.data += packages

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
                    for act in self.on_send:
                        act(self.sending_bit)
                self.send_time += 1
                if self.send_time == self.signal_time:
                    self.package_index += 1
                    if self.package_index == len(self.current_package):
                        self.current_package = []              
                    self.send_time = 0

        if self.is_sending:
            return

        elif self.time_connected % self.signal_time//3 == 0:
            bit = self.cable_head.receive()
            if bit is not None:
                self.recived_bits.append(bit)

        if self.time_connected % self.signal_time == 0 and self.recived_bits:
            temp = [(v,k) for k,v in Counter(self.recived_bits).items()]
            for act in self.on_receive:
                act(max(temp)[1])
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
            self.package_index = 0
            self.send_time = 0
            self.is_sending = False
            for act in self.on_collision:
                act()
            return True
        return False

    def disconnect(self):
        self.data.insert(0, self.current_package)
        self.current_package = []
        self.package_index = 0
        self.is_sending = False
        self.send_time = 0
        self.sending_bit = 0
        self.max_time_to_send = 16
        self.time_connected = 0
        self.recived_bits = []