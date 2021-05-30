import abc
from typing import List
from nesim.frame import Frame
from nesim.devices import Device


class FrameSender(Device, metaclass=abc.ABCMeta):

    mac: List[int] = []

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

        sr = self.ports[self.port_name(port)]
        sr.send(packages)

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
        frame_bit_data = Frame.build(mac, self.mac, data).bit_data
        self.send(frame_bit_data, port=port)
