from OOP_sheep_animation_path import Simulation
import numpy as np
from utils import read_path_from_file

# parameters
T = 1000.
dt = 0.025

# simulation configuration
a = Simulation()
tracking_speed = 1.1
points = read_path_from_file("path_points.txt")

a.add_dog([.9 , 0.4])
a.add_dog([.3 , 0.5])
a.add_dog([.4 , 0.6])
a.add_dog([.0 , 0.])
a.add_dog([-.1 , 0.2])
a.add_dog([-.2 , 0.3])
a.initial_configurations(dt, tracking_speed)
a.add_drones(5, initial_area=5, center=a.center_trail[0])
a.add_sheeps(20, 3)
a.enter_path(points)
print("lost sheep:", len(a.lose_sheeps))

# simuation
a.simulate(T, dt)

#input("Press Enter to continue...")

#animation
a.animate_coppelia()
