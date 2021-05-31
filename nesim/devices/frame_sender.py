import abc
from typing import Dict, List
from nesim.devices.multiple_port_device import MultiplePortDevice
from nesim.frame import Frame


class FrameSender(MultiplePortDevice, metaclass=abc.ABCMeta):
    """
    Representa un dispositivo capaz de enviar frames.

    Attributes
    ----------
    mac_addrs: Dict[int, List[int]]
        Tabla que contiene la dirección MAC de cada puerto.
    """

    def __init__(self, name: str, ports_count: int, signal_time: int):
        self.mac_addrs: Dict[int, List[int]] = {}
        super().__init__(name, ports_count, signal_time)

    def send(self, data: List[int], package_size = None, port: int = 1):
        """
        Agrega nuevos datos para ser enviados a la lista de datos.

        Parameters
        ----------
        data : List[List[int]]
            Datos a ser enviados.
        """

        if package_size is None:
            package_size = len(data)

        packages = []
        while data:
            packages.append(data[:package_size])
            data = data[package_size:]

        send_receiver = self.ports[self.port_name(port)]
        send_receiver.send(packages)

    def send_frame(self, mac: List[int], data: List[int], port: int = 1):
        """
        Ordena a un host a enviar un frame determinado a una dirección mac
        determinada.

        Parameters
        ----------
        host_name : str
            Nombre del host que envía la información.
        mac : List[int]
            Mac destino.
        data : List[int]
            Frame a enviar.
        """

        frame = Frame.build(mac, self.mac_addrs[port], data)
        print(f'[{self.sim_time:>6}] {self.name + " - " + str(port):>18}      send: {frame}')
        self.send(frame.bit_data, port=port)
