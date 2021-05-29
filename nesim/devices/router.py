from typing import List, Union
from nesim.devices.multiple_port_device import MultiplePortDevice
from nesim.frame import Frame
from nesim.ip import IP


class Route():

    def __init__(self, destination_ip: IP, mask: IP, gateway: IP,
                 interface: int) -> None:
        self.destination_ip = destination_ip
        self.mask = mask
        self.gateway = gateway
        self.interface = interface

    def enroute(self, ip: IP) -> bool:
        masked_ip = ip.raw_value & self.mask.raw_value
        if masked_ip == self.destination_ip:
            return True
        return False

    def __eq__(self, other: object) -> bool:
        return self.destination_ip == other.destination_ip and \
               self.mask == other.mask and \
               self.gateway == other.gateway and \
               self.interface == other.interface

    def __str__(self) -> str:
        return f'{self.destination_ip} {self.mask} {self.gateway} {self.interface}'


class RouteTable():
    """Tabla de rutas"""

    routes: List[Route] = []

    def reset(self) -> None:
        """Limpia la tabla de rutas."""

        self.routes.clear()

    def add_route(self, route: Route) -> None:
        """
        Agrega una ruta a la tabla de rutas.

        Parameters
        ----------
        route : Route
            Ruta a añadir.
        """

        self.routes.append(route)
        self.routes.sort(lambda x: x.mask.raw_value, reverse=True)

    def remove_route(self, route: Route) -> None:
        """
        Elimina una ruta de la tabla de rutas.

        Parameters
        ----------
        route : Route
            Ruta a eliminar.
        """

        if route in self.routes:
            self.routes.remove(route)

    def get_enrouting(self, ip: IP) -> Union[Route, None]:
        """
        Obtiene la ruta según la prioridad de las mismas dado un IP.

        Parameters
        ----------
        ip : IP
            Ip a enrutar.

        Returns
        -------
        Union[Route, None]
            Ruta obtenida. None en caso de no existir ninguna ruta.
        """

        for route in self.routes:
            if route.enroute(ip):
                return route
        return None


class Router(MultiplePortDevice, RouteTable):
    """Representa un router en la simulación."""

    def on_frame_received(self, frame: Frame, port: str) -> None:
        raise NotImplementedError()
