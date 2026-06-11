import time
from sim import Sim
from renderer import Renderer

# 0.1 ms dt
dt = 0.0001
simulation = Sim("F15.eng", dt) 

# 30 seconds
x, y, z, q = simulation.simulate(30, "output.csv")

# Render
render = Renderer("output.csv")
time.sleep(2)
render.animate(dt, 50)
