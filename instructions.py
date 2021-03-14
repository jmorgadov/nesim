import abc
import simulation as sim
import devices as dv
from typing import List


class Instruction(metaclass=abc.ABCMeta):

    def __init__(self, time: int):
        self.time = time

    @abc.abstractmethod
    def execute(self, net_sim: sim.NetSimulation):
        pass
        

class CreateHubIns(Instruction):

    def __init__(self, time: int, hub_name: str, ports_count: int):
        super().__init__(time)
        self.hub_name = hub_name
        self.ports_count = ports_count

    def execute(self, net_sim: sim.NetSimulation):
        hub = dv.Hub(self.hub_name, self.ports_count)
        net_sim.add_device(hub)


class CreateHostIns(Instruction):

    def __init__(self, time: int, host_name: str):
        super().__init__(time)
        self.host_name = host_name
    
    def execute(self, net_sim: sim.NetSimulation):
        host = dv.PC(self.host_name, sim.SIGNAL_TIME)
        net_sim.add_device(host)

class ConnectIns(Instruction):

    def __init__(self, time: int, port1: str, port2: str):
        super().__init__(time)
        self.port1 = port1
        self.port2 = port2

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.connect(self.port1, self.port2)
    

class SendIns(Instruction):
    
    def __init__(self, time: int, host_name: str, data: List[int]):
        super().__init__(time)
        self.host_name = host_name
        self.data = data

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.send(self.host_name, self.data) 

class DisconnectIns(Instruction):
    """
    
    """
    def __init__(self, time: int, port_name: str):
        super().__init__(time)
        self.port_name = port_name

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.disconnect(self.port_name)
    
