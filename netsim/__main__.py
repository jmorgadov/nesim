import netsim

if __name__ == '__main__':
    raw_instr = [
        '0 create hub H 4',
        '0 create host PCA',
        '0 create host PCB',
        '0 connect PCA_1 H_1',
        '0 connect PCB_1 H_2',
        '0 send PCA 00110101'
    ]
    instr = netsim.parse_instructions(raw_instr)
    sim = netsim.NetSimulation()
    sim.start(instr)
