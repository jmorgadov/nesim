import abc
import nesim.simulation as sim
import nesim.devices as dv
from typing import List


class Instruction(metaclass=abc.ABCMeta):
    """
    Representación general de una instrucción.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    """

    def __init__(self, time: int):
        self.time = time

    @abc.abstractmethod
    def execute(self, net_sim: sim.NetSimulation):
        """
        Ejecuta la instrucción en una simulación dada.

        Parameters
        ----------
        net_sim : sim.NetSimulation
            Simulación en la que será ejecutada la instrucción.
        """
        

class CreateHubIns(Instruction):
    """
    Instrucción para crear un Hub.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    hub_name : str
        Nombre del hub.
    ports_count : int
        Cantidad de puertos del hub.
    """

    def __init__(self, time: int, hub_name: str, ports_count: int):
        super().__init__(time)
        self.hub_name = hub_name
        self.ports_count = ports_count

    def execute(self, net_sim: sim.NetSimulation):
        hub = dv.Hub(self.hub_name, self.ports_count)
        net_sim.add_device(hub)


class CreateHostIns(Instruction):
    """
    Instrucción para crear un Host.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    host_name : str
        Nombre del host.
    """

    def __init__(self, time: int, host_name: str):
        super().__init__(time)
        self.host_name = host_name

    def execute(self, net_sim: sim.NetSimulation):
        host = dv.Host(self.host_name, net_sim.signal_time)
        net_sim.add_device(host)

class CreateSwitchIns(Instruction):
    """
    Instrucción para crear un Switch.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    switch_name : str
        Nombre del switch.
    ports_count : int
        Cantidad de puertos del switch.
    """

    def __init__(self, time: int, switch_name: str, ports_count: int):
        super().__init__(time)
        self.switch_name = switch_name
        self.ports_count = ports_count

    def execute(self, net_sim: sim.NetSimulation):
        switch = dv.Switch(self.switch_name, self.ports_count, 
                           net_sim.signal_time)
        net_sim.add_device(switch)


class ConnectIns(Instruction):
    """
    Instrucción para conectar dos puertos.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    port1, port2 : str
        Nombre de los puertos a conectar.
    """

    def __init__(self, time: int, port1: str, port2: str):
        super().__init__(time)
        self.port1 = port1
        self.port2 = port2

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.connect(self.port1, self.port2)


class SendIns(Instruction):
    """
    Instrucción para ordenar a un host a enviar información.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    host_name : str
        Nombre del host que enviará los datos.
    data : List[int]
        Datos a enviar.
    """
    def __init__(self, time: int, host_name: str, data: List[int]):
        super().__init__(time)
        self.host_name = host_name
        self.data = data

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.send(self.host_name, self.data)


class DisconnectIns(Instruction):
    """
    Instrucción para desconectar un puerto.

    Parameters
    ----------
    time : int
        Timepo en milisegundos en el que será ejecutada la instrucción en
        la simulación.
    port_name : str
        Nombre del puerto al que se le desconectará el cable.
    """
    def __init__(self, time: int, port_name: str):
        super().__init__(time)
        self.port_name = port_name

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.disconnect(self.port_name)


class MacIns(Instruction):
    def __init__(self, time: int, host_name: str, address: List[int]):
        super().__init__(time)
        self.host_name = host_name
        self.address = address
    
    def execute(self, net_sim: sim.NetSimulation):
        net_sim.assign_mac_addres(self.host_name, self.address)

class SendFrameIns(Instruction):
    def __init__(self, time: int, host_name: str, mac: List[int],
                 data: List[int]):
        super().__init__(time)
        self.host_name = host_name
        self.mac = mac
        self.data = data

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.send_frame(self.host_name, self.mac, self.data)
