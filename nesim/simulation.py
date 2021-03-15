from typing import Dict, List
from nesim.devices import Device, PC, Cable
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
        self.hosts: Dict[str, PC] = {}
        self.end_delay = self.signal_time
    
    @property
    def is_running(self):
        """
        bool : Indica si la simulación todavía está en ejecución.
        """

        device_sending = any([(d.is_sending or d.time_to_send) \
             for d in self.hosts.values()])
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

        if isinstance(device, PC):
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

        cab = Cable()
        dev1 = self.port_to_device[port1]
        dev2 = self.port_to_device[port2]

        if dev1.name in self.disconnected_devices.keys():
            self.disconnected_devices.pop(dev1.name)
            self.add_device(dev1)
        if dev2.name in self.disconnected_devices.keys():
            self.disconnected_devices.pop(dev2.name)
            self.add_device(dev2)

        dev1.sim_time = self.time
        dev2.sim_time = self.time
        self.port_to_device[port1].connect(cab, port1)
        self.port_to_device[port2].connect(cab, port2)

    def send(self, host_name: str, data: List[int]):
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

        self.hosts[host_name].send(data)

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

        for cable in dev.ports.values():
            if cable is not None:
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

    def update(self):
        """
        Ejecuta un ciclo de la simulación actualizando el estado de la
        misma.

        Esta función se ejecuta una vez por cada milisegundo simulado.
        """
        # print(self.time, self.devices)
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
                if device not in self.hosts.values():
                    device.update(self.time)

        for host in self.hosts.values():
            host.receive()
        
        self.time += 1
