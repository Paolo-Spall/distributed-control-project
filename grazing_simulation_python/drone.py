import numpy as np
from utils import random_2d_vector

class Drone:
    def __init__(self, initial_area, center, simulation):
        self.P = random_2d_vector() * initial_area + center
        self.V = np.array([0, 0])
        self.marker = 'p'
        self.sim = simulation
        self.trail = []
        self.trailV = []
        self.trail_marker = []
        self.trail_marker.append(self.marker)

        self.trail.append(self.P)

    def step(self, dt, p_des):
        self.V = p_des - self.P
        self.P = self.P + self.V * dt
        self.trail.append(self.P)
        self.trailV.append(self.V)
        self.trail_marker.append(self.marker)