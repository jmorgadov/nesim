import simulation as sim
import inst_parser as prs
import logging

logging.basicConfig(
    format='%(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    netsim = sim.NetSimulation()
    with open('input.txt', 'r') as f:
        instr = prs.parse_instructions(f.readlines())
        netsim.start(instr)

