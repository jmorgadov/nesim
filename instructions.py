import abc
import simulation as sim
import devices as dv
class Instruction(metaclass=abc.ABCMeta):

    def __init__(self, time):
        self.time = time

    @abc.abstractmethod
    def execute(self, net_sim: sim.NetSimulation):
        pass
        

class CreateHubIns(Instruction):

    def __init__(self, time, hub_name, ports):
        super().__init__(time)
        self.hub_name = hub_name
        self.ports = ports

    def execute(self, net_sim: sim.NetSimulation):
        hub = dv.Hub(self.hub_name, self.ports)
        net_sim.add_device(hub)


class CreateHostIns(Instruction):

    def __init__(self, time, host_name):
        super().__init__(time)
        self.host_name = host_name
    
    def execute(self, net_sim: sim.NetSimulation):
        host = dv.PC(self.host_name, sim.SIGNAL_TIME)
        net_sim.add_device(host)

class ConnectIns(Instruction):

    def __init__(self, time, port1, port2):
        super().__init__(time)
        self.port1 = port1
        self.port2 = port2

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.connect(self.port1, self.port2)
    

class SendIns(Instruction):
    
    def __init__(self, time, host_name, data):
        super().__init__(time)
        self.host_name = host_name
        self.data = data

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.send(self.host_name, self.data) 

class DisconnectIns(Instruction):

    def __init__(self, time, port_name):
        super().__init__(time)
        self.port_name = port_name

    def execute(self, net_sim: sim.NetSimulation):
        net_sim.disconnect(self.port_name)
    
