# example.py

import nesim

raw_instr = []
with open('script.txt', 'r') as file:
    raw_instr = file.readlines()

instr = nesim.parse_instructions(raw_instr)
sim = nesim.NetSimulation()
sim.start(instr)
