import simulation as sim
import inst_parser as prs
import logging

logging.basicConfig(
    format='[%(levelname)s] %(message)s',
    level=logging.INFO
)

netsim = sim.NetSimulation()

instr = []
with open('input.txt', 'r') as f:
    instr = prs.parse_instructions(f.readlines())

netsim.start(instr)