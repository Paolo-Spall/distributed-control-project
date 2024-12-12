from OOP_sheep_animation_path import Simulation
import numpy as np

# parameters
T = 1000.
dt = 0.025

# simulation configuration
a = Simulation()
tracking_speed = 1.1
points = [[-10, 10.], [0., 0.]]  # , (-100, -200), (-50, -100), (0, -50), (50, 50), (100, 100), (150, 150), (200, 200)]
points = [np.array(i) for i in points]
a.add_dog([9.9 - 20, 0.4])
a.add_dog([10.3 - 20, 0.5])
a.add_dog([10.4 - 20, 0.6])
a.add_dog([10 - 20, 0])
a.add_dog([-10.1 - 20, 0.2])
a.add_dog([-10 - 20, 0.3])
a.initial_configurations(dt, tracking_speed)
a.add_drones(5, initial_area=5, center=a.center_trail[0])
a.add_sheeps(20, 3)
a.enter_path(points)

# simuation
a.simulate(T, dt)
print("lost sheep:", len(a.lose_sheeps))

#input("Press Enter to continue...")

#animation
a.animate(grid_dimension=80)