# example.py

import nesim

instr = nesim.load_instruccions()
sim = nesim.NetSimulation()
sim.start(instr)
