import netsim

if __name__ == '__main__':
    sim = netsim.NetSimulation()
    with open('input.txt', 'r') as f:
        instr = netsim.parse_instructions(f.readlines())
        sim.start(instr)
