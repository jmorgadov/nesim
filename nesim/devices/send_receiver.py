from random import randint
from typing import List
from collections import Counter
from nesim.devices.cable import DuplexCableHead


class SendReceiver():
    """
    Componente capaz de recibir y enviar información a través de un cable
    duplex.

    Parameters
    ----------
    signal_time : int
        Tiempo mínimo que debe estar un bit en transmisión.
    cable_head : DuplexCableHead
        Extremo del cable duplex al que se encuentra conectado.

    Attributes
    ----------
    data : List[int]
        Datos a enviar.
    """

    def __init__(self, signal_time: int, cable_head: DuplexCableHead = None):
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

    @property
    def is_active(self):
        """bool : Estado del ``SendReceiver``."""
        return self.is_sending or self.time_to_send

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
                self.sending_bit = None
                self.is_sending = False
                self.cable_head.send(None)

    def update(self):
        """
        Actualiza el estado de la información.
        """

        self.time_connected += 1

        if self.cable_head is None:
            return

        self.load_package()

        if self.time_to_send:
            self.time_to_send -= 1

        if self.time_to_send:
            return

        if self.current_package:
            self.is_sending = True
            self.sending_bit = self.current_package[self.package_index]
            self.cable_head.send(self.sending_bit)


    def send(self, data: List[List[int]]):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[List[int]]
            Datos a ser enviados.
        """
        self.data += data

    def receive(self):
        """
        Lee del cable al que está conectado.

        Si se encuentra enviando infromación entonces comprueba que no
        haya colisión.

        En caso contrario almacena la lectura del cable en varios ocasiones
        entre un ``SIGNAL_TIME`` y el siguiente. Al concluir el ``SIGNAL_TIME``
        se guarda como lectura final la moda de los datos almacenados.
        """

        if self.cable_head is None:
            return

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

            if self.cable_head.send_cable == self.cable_head.receive_cable:
                return

        if self.time_connected % self.signal_time//3 == 0:
            bit = self.cable_head.receive()
            if bit is not None:
                self.recived_bits.append(bit)

        if self.time_connected % self.signal_time == 0 and self.recived_bits:
            temp = [(v,k) for k,v in Counter(self.recived_bits).items()]
            received = max(temp)[1]
            for act in self.on_receive:
                act(received)
            self.recived_bits = []

    def check_collision(self):
        """
        Comprueba si existe una colisión.

        Returns
        -------
        bool
            ``True`` si hubo colisión, ``False`` en caso contrario.
        """

        if self.is_sending and self.cable_head.send_value != self.sending_bit:
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
        """
        Desconecta el ``SendReceiver``.
        """

        # Reset data in cable head
        self.cable_head.receive_cable.value = None
        self.cable_head.send_cable.value = None
        self.cable_head = None

        # Reset sending info
        if self.current_package:
            self.data.insert(0, self.current_package)
        self.current_package = []
        self.package_index = 0
        self.is_sending = False
        self.send_time = 0
        self.sending_bit = None
        self.max_time_to_send = 16
        self.time_connected = 0
        self.recived_bits = []
