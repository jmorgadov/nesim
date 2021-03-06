import abc

class Instruction(metaclass=abc.ABCMeta):

    def __init__(self, time, name, args):
        self.time = time
        self.name = name
        self.args = args

    @abc.abstractmethod
    def execute(self, net_sim):
        pass
