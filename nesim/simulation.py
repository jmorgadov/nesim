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
            raise ValueError(f'The device name {device.name} is already taken.')

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

        packages = []
        while data:
            packages.append(data[:package_size])
            data = data[package_size:]

        if host_name not in self.hosts.keys():
            raise ValueError(f'Unknown host {host_name}')

        self.hosts[host_name].send(packages)

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

        size_str = f'{len(data)//8:b}'
        data_size = [0]*8

        for i in range(1,len(size_str) + 1):
            data_size[-i] = int(size_str[-i])

        final_data = mac + self.hosts[host_name].mac + data_size + [0]*8 + data

        self.send(host_name, final_data, len(final_data))

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

    def assign_mac_addres(self, host_name, mac):
        """
        Asigna una dirección mac a un host.

        Parameters
        ----------
        host_name : str
            Nombre del host al cual se le asigna la dirección mac.
        mac : List[int]
            Dirección mac.
        """

        self.hosts[host_name].mac = mac

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

        for _ in range(len(self.devices)):
            for device in self.devices.values():
                if isinstance(device, Hub):
                    device.update(self.time)

        for dev in self.devices.values():
            if isinstance(dev, Switch):
                dev.update(self.time)

        for host in self.hosts.values():
            host.receive()

        self.time += 1
