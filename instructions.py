import abc

class Instruction(metaclass=abc.ABCMeta):

    def __init__(self, time):
        self.time = time

    @abc.abstractmethod
    def execute(self, net_sim):
        pass
        

class CreateHubIns(Instruction):

    def __init__(self, time, hub_name, ports):
        super(Instruction, self).__init__(time)
        self.hub_name = hub_name
        self.ports = ports


class CreateHostIns(Instruction):

    def __init__(self, time, host_name):
        super(Instruction, self).__init__(time)
        self.host_name = host_name

class ConnectIns(Instruction):

    def __init__(self, time, port1, port2):
        super(Instruction, self).__init__(time)
        self.port1 = port1
        self.port2 = port2
    

class SendIns(Instruction):
    
    def __init__(self, time, host_name, data):
        super(Instruction, self).__init__(time)
        self.host_name = host_name
        self.data = data

class DisconnectIns(Instruction):

    def __init__(self, time, port_name):
        super(Instruction, self).__init__(time)
        self.port_name = port_name
    
