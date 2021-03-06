

class NetSimulation():

    def __init__(self, instructions, signal_time=10, output_path='.'):
        self.instructions = instructions
        self.signal_time = signal_time
        self.output_path = output_path
        self.time = 0
        self.inst_index = 0
        

    def start(self):
        self.time = 0
        self.inst_index = 0
        pass

    def update(self):
        t = self.time

        current_insts = []
        while self.inst_index < len(self.instructions) and
              t == self.instructions[self.inst_index].time:
            current_insts.append(self.instructions[self.inst_index])
            self.inst_index += 1            

        for instr in current_insts:
            instr.execute(self)

        
        self.time += 1
