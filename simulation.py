

class NetSimulation():

    def __init__(self, signal_time=10, output_path='.'):
        self.instructions = []
        self.signal_time = signal_time
        self.output_path = output_path
        self.time = 0
        self.inst_index = 0
        self.pending_devices = []


    def start(self, instructions):
        self.instructions = instructions
        self.time = 0
        pass

    def update(self):
        t = self.time

        current_insts = []
        while self.instructions and t == self.instructions[0].time:
            current_insts.append(self.instructions.pop(0))           

        for instr in current_insts:
            instr.execute(self)

        
        self.time += 1
