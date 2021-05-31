from io import UnsupportedOperation
from nesim.devices.ip_packet_sender import IPPacketSender
from nesim.devices.router import Route, Router
from nesim.ip import IP
from typing import Dict, List
from nesim.devices.switch import Switch
from nesim.devices.hub import Hub
from nesim.devices import Device, Duplex, Host
import nesim.utils as utils


class NetSimulation():
    """
    Clase principal encargada de ejecutar una simulación.

    Parameters
    ----------
    output_path : str
        Ruta donde se guardarán los logs de la simulación al finalizar.
        la misma. (Por defecto es ``output``).
    """

    def __init__(self, output_path: str = 'output'):
        utils.check_config()
        self.instructions = []
        self.signal_time = utils.CONFIG['signal_time']
        self.output_path = output_path
        self.inst_index = 0
        self.time = 0
        self.pending_devices = []
        self.port_to_device: Dict[str, Device] = {}
        self.devices: Dict[str, Device] = {}
        self.disconnected_devices: Dict[str, Device] = {}
        self.hosts: Dict[str, Host] = {}
        self.end_delay = self.signal_time

    @property
    def is_running(self):
        """
        bool : Indica si la simulación todavía está en ejecución.
        """

        device_sending = any([d.is_active for d in self.devices.values()])
        running = self.instructions or device_sending
        if not running:
            self.end_delay -= 1
        return self.end_delay > 0

    def add_device(self, device: Device):
        """
        Añade un dispositivo a la simulación.

        Parameters
        ----------
        device : Device
            Dispositivo a añadir.
        """

        if device.name in self.devices.keys():
            raise ValueError(
                f'The device name {device.name} is already taken.')

        self.devices[device.name] = device

        if isinstance(device, Host):
            self.hosts[device.name] = device

        for port in device.ports.keys():
            self.port_to_device[port] = device

    def connect(self, port1, port2):
        """
        Conecta dos puertos mediante un cable.

        Parameters
        ----------
        port1, port2 : str
            Nombres de los puertos a conectar.
        """

        if port1 not in self.port_to_device.keys():
            raise ValueError(f'Unknown port {port1}')

        if port2 not in self.port_to_device.keys():
            raise ValueError(f'Unknown port {port2}')

        dev1 = self.port_to_device[port1]
        dev2 = self.port_to_device[port2]

        if dev1.name in self.disconnected_devices.keys():
            self.disconnected_devices.pop(dev1.name)
            self.add_device(dev1)
        if dev2.name in self.disconnected_devices.keys():
            self.disconnected_devices.pop(dev2.name)
            self.add_device(dev2)

        is_simple = isinstance(dev1, Hub) or isinstance(dev2, Hub)
        cab = Duplex(simple=is_simple)
        dev1.sim_time = self.time
        dev2.sim_time = self.time
        self.port_to_device[port1].connect(cab.head_1, port1)
        self.port_to_device[port2].connect(cab.head_2, port2)

    def send(self, host_name: str, data: List[int],
             package_size: int = 8):
        """
        Ordena a un host a enviar una serie de datos determinada.

        Parameters
        ----------
        host_name : str
            Nombre del host que enviará la información.
        data : List[int]
            Datos a enviar.
        """

        if host_name not in self.hosts.keys():
            raise ValueError(f'Unknown host {host_name}')

        self.hosts[host_name].send(data, package_size)

    def send_frame(self, host_name: str, mac: List[int], data: List[int]):
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

        if host_name not in self.hosts.keys():
            raise ValueError(f'Unknown host {host_name}')

        self.hosts[host_name].send_frame(mac, data)

    def send_ip_package(self, host_name: str, ip_dest: IP, data: List[int]):
        """
        Env'ia un paquete IP a una dirección determinada.

        Parameters
        ----------
        host_name : str
            Host que envía el paquete.
        ip_dest : IP
            Dirección IP destino.
        data : List[int]
            Datos a enviar.

        Raises
        ------
        ValueError
            Si el host no existe.
        """

        if host_name not in self.hosts.keys():
            raise ValueError(f'Unknown host {host_name}')

        self.hosts[host_name].send_by_ip(ip_dest, data)

    def ping_to(self, host_name: str, ip_dest: IP):
        """
        Ejecuta la instrucción ``ping``.

        Parameters
        ----------
        host_name : str
            Host que ejecuta la acción.
        ip_dest : IP
            IP destino.

        Raises
        ------
        ValueError
            Si el host no existe.
        """

        if host_name not in self.hosts.keys():
            raise ValueError(f'Unknown host {host_name}')

        self.hosts[host_name].send_ping_to(ip_dest)

    def route(self, device_name: str, action: str = 'reset',
              route: Route = None):
        """
        Ejecuta una de las acciones realcionadas con las rutas: ``add``,
        ``remove``, ``reset``

        Parameters
        ----------
        device_name : str
            Nombre del dispositivo al que se le ejecuta la acción.
        action : str, optional
            Acción a ejecutar.
        route : Route, optional
            Ruta a añadir o eliminar.
        """

        router: Router = self.devices[device_name]
        if action == 'add':
            router.add_route(route)
        elif action == 'remove':
            router.remove_route(route)
        else:
            router.reset_routes()

    def disconnect(self, port: str):
        """
        Desconecta un puerto.

        Parameters
        ----------
        port : str
            Puerto a desconectar.
        """

        if port not in self.port_to_device.keys():
            raise ValueError(f'Unknown port {port}')

        dev = self.port_to_device[port]
        dev.disconnect(port)

        if dev.name in self.hosts.keys():
            self.hosts.pop(dev.name)
            self.devices.pop(dev.name)
            self.disconnected_devices[dev.name] = dev
            return

        if isinstance(dev, Hub):
            for cable in dev.ports.values():
                if cable is not None:
                    break
            else:
                self.devices.pop(dev.name)
                self.disconnected_devices[dev.name] = dev

        if isinstance(dev, Switch):
            for send_receiver in dev.ports.values():
                if send_receiver.cable_head is not None:
                    break
            else:
                self.devices.pop(dev.name)
                self.disconnected_devices[dev.name] = dev

    def start(self, instructions):
        """
        Comienza la simulación dada una lista de instrucciones.

        Parameters
        ----------
        instructions : List[Instruction]
            Lista de instrucciones a ejecutar en la simulación.
        """

        self.instructions = instructions
        self.time = 0
        while self.is_running:
            self.update()
        for device in self.devices.values():
            device.save_log(self.output_path)

    def assign_mac_addres(self, device_name, mac, interface):
        """
        Asigna una dirección mac a un host.

        Parameters
        ----------
        device_name : str
            Nombre del dispositivo al cual se le asigna la dirección mac.
        mac : List[int]
            Dirección mac.
        """

        self.devices[device_name].mac_addrs[interface] = mac

    def assign_ip_addres(self, device_name, ip: IP, mask: IP, interface: int):
        """
        Asigna una dirección mac a un host.

        Parameters
        ----------
        device_name : str
            Nombre del dispositivo al cual se le asigna la dirección mac.
        mac : List[int]
            Dirección mac.
        """

        device: IPPacketSender = self.devices[device_name]
        if not isinstance(device, IPPacketSender):
            raise UnsupportedOperation(f'Can not set ip to {device_name}')

        device.ips[interface] = ip
        device.masks[interface] = mask

    def update(self):
        """
        Ejecuta un ciclo de la simulación actualizando el estado de la
        misma.

        Esta función se ejecuta una vez por cada milisegundo simulado.
        """

        current_insts = []
        while self.instructions and self.time == self.instructions[0].time:
            current_insts.append(self.instructions.pop(0))

        for instr in current_insts:
            instr.execute(self)

        for device in self.devices.values():
            device.reset()

        for host in self.hosts.values():
            host.update(self.time)

        for dev in self.devices.values():
            if isinstance(dev, Switch) or type(dev) == Router:
                dev.update(self.time)

        for _ in range(len(self.devices)):
            for device in self.devices.values():
                if isinstance(device, Hub):
                    device.update(self.time)

        for dev in self.devices.values():
            if isinstance(dev, Switch) or type(dev) == Router:
                dev.receive()

        for host in self.hosts.values():
            host.receive()

        self.time += 1
