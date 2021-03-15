# example.py

import nesim

instr = nesim.load_instructions()
sim = nesim.NetSimulation()
sim.start(instr)
