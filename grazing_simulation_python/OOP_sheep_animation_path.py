import numpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib  # Importing matplotlib
matplotlib.use('TkAgg')  # Setting the backend for matplotlib to TkAgg
from agents import Sheep, Dog
from drone import Drone
from utils import limit_decimal_places
from coverage import bounded_voronoi, centroid_region
import time
import sys  # Importing sys module for system-specific parameters and functions
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class Simulation:
    l_coverage = 15.

    def __init__(self):
        self.simulation_on = True
        self.sheeps = []
        self.dogs = []
        self.dogs_form = []
        self.drones = []
        self.iter_steps_n = 0
        self.center = np.array([0., 0.])
        #self.center_V = np.array([0, 0])
        self.lose_sheeps = []
        self.herd_dist_limit = 8.5 #distanza alla quale una pecotra viene considerata persa
        self.center_trail = []
        self.trajectory_trail = []
        self.bounding_box = np.array([-self.l_coverage + self.center[0], self.l_coverage + self.center[0],
                                      -self.l_coverage + self.center[1], self.l_coverage+self.center[1]])
        # [x_min, x_max, y_min, y_max]
        self.chasing_assignment = []

    def initial_configurations(self, dt, speed):
        self.tracking_speed = speed
        self.tracking_velocity = np.zeros(2)
        self.formation_control_on()
        for t in range(0, 20):
            for dog in self.dogs:
                dog.step(dt)
        for dog in self.dogs:
            dog.trail.clear()
            dog.trail_marker.clear()
            dog.color_trail.clear()
            dog.pd_trail.clear()
        self.compute_dog_center()



    def enter_path(self, points):
        """biuld the path for the sheeps to follow"""
        self.original_path = self.center_trail + points + self.center_trail
        self.tracked_point = points.pop(0) # firt point to be tracked
        self.path =  points + [self.center_trail[0]]


    def add_sheeps(self, n, initial_area):
        for i in range(n):
            self.sheeps.append(Sheep(initial_area, self.center_trail[0], self))
    
    def add_dog(self, P):
        dog = Dog(P, self)
        self.dogs.append(dog)
        self.dogs_form.append(dog)

    def add_drones(self, n, initial_area, center):
        for i in range(n):
            self.drones.append(Drone(initial_area, center, self))


    def compute_dog_center(self):
        count = 0
        center = numpy.array([0, 0])
        for dog in self.dogs_form:
            center = center+dog.P
        self.center = center / len(self.dogs_form)
        self.center_trail.append(self.center)
        self.compute_bounding_box()

    def compute_formation_trajectory(self, i, c):
        dist = c[i] - self.center
        return dist

    def compute_bounding_box(self):
        self.bounding_box = np.array([-self.l_coverage + self.center[0], self.l_coverage + self.center[0],
                                      -self.l_coverage + self.center[1], self.l_coverage + self.center[1]])


    #def compute_center_velocity(self, dt):
    #    if len(self.center_trail) > 1:
    #        self.center_V = (self.center_trail[-1] - self.center_trail[-2])/dt

    def formation_control_on(self):
        for dog in self.dogs_form:
            dog.formation_flag = True

    def formation_control_off(self):
        for dog in self.dogs_form:
            dog.formation_flag = False

    def assign_chasing_dogs(self):
        self.chasing_assignment.clear()
        for sheep in self.lose_sheeps:
            dist = 1000
            dist_pusher = 1000
            chased_sheep = sheep
            chasing_dog = None
            dog_pusher = None # cane che spinge il branco
            i = 0
            for dog in self.dogs:
                if not dog.chasing_sheep:
                     i += 1
                     if i == 1:
                         dist_pusher = np.linalg.norm(sheep.P - dog.P)
                     else:
                        if np.linalg.norm(sheep.P - dog.P) < dist_pusher:
                            chasing_dog = dog_pusher
                            dog_pusher = dog
                            dist = dist_pusher
                            dist_pusher = np.linalg.norm(sheep.P - dog.P)
            if chasing_dog is not None:
                self.chasing_assignment.append([chasing_dog, chased_sheep])
                chasing_dog = None


    
    def track_path(self):
        """compute the common control input for the dogs to track the path"""
        distance = self.tracked_point - self.center_trail[-1]
        dist_norm = np.linalg.norm(distance)
        direction = distance / dist_norm # direction unit vector
        self.tracking_velocity = direction * self.tracking_speed
        if dist_norm < 0.5:
            if self.path:
                self.tracked_point = self.path.pop(0)
            else:
                self.simulation_on = False
                
        

    def compute_coverage_drones(self):
        eps = sys.float_info.epsilon  # Getting the smallest representable positive number

        drones_pos = np.array([drone.P for drone in self.drones])  # Getting positions of drones
        vor = bounded_voronoi(drones_pos, self.bounding_box)

        centroids = []  # Initializing list for centroids
        for region in vor.filtered_regions:
            vertices = vor.vertices[region + [region[0]], :]
            centroid = centroid_region(vertices)
            # centroid = compute_centroid(vertices, 0.1, [0.6,0.6])
            centroids.append(list(centroid[0, :]))
        if len(centroids) < len(self.drones):
            for i in range(len(self.drones) - len(centroids)):
                centroids.append(self.center)

        return centroids  # Returning centroids


    def step(self, dt, i):
        self.compute_dog_center()
        self.track_path()
        #self.compute_center_velocity(dt)
        self.assign_chasing_dogs()
        #print(self.chasing_assignment)
        for dog in self.dogs:
            dog.step(dt)
        for sheep in self.sheeps:
            sheep.step(dt,self.dogs)

        p_des_drones = self.compute_coverage_drones()

        for drone, p_des_drone  in zip(self.drones, p_des_drones):
            drone.step(dt, p_des_drone)



    def simulate(self, T, dt):
        
        self.dt = dt
        t = 0.
        while self.simulation_on:
            self.step(dt, int(t/dt))
            self.iter_steps_n += 1
            t += dt
        print("time",t)

    def entities(self):
        return self.sheeps + self.dogs + self.drones

    def animate(self, grid_dimension=50):
        for i in range(self.iter_steps_n):
            plt.clf()
            plt.xlim(-grid_dimension/2,grid_dimension/2)
            plt.ylim(-grid_dimension/2,grid_dimension/2)
            '''plt.xlim(self.center_trail[i][0]-25., self.center_trail[i][0]+25.)
            plt.ylim(self.center_trail[i][1]-25., self.center_trail[i][1]+25.)'''
            plt.scatter(self.center_trail[i][0],self.center_trail[i][1],marker="*")
            plt.gca().add_patch(patches.Circle((self.center_trail[i][0],self.center_trail[i][1]),
                                               radius=7.5, edgecolor='green', facecolor='none', linewidth=2))
            plt.gca().add_patch(patches.Circle((self.center_trail[i][0], self.center_trail[i][1]),
                                               radius=self.herd_dist_limit, edgecolor='red', facecolor='none', linewidth=2))
            plt.gca().add_patch(patches.Rectangle((self.center_trail[i][0]-self.l_coverage,
                                                   self.center_trail[i][1]-self.l_coverage), self.l_coverage*2,
                                                   self.l_coverage*2, edgecolor='blue', facecolor='none', linewidth=2))

            for agent in self.entities():
                plt.scatter(agent.trail[i][0], agent.trail[i][1], marker=agent.trail_marker[i])
            plt.text(0.95, 0.95, limit_decimal_places(i*self.dt,2), fontsize=12, bbox=dict(facecolor='white', alpha=0.5),
                     horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)
            original_path_arr = np.array(self.original_path)
            plt.plot(original_path_arr[:, 0], original_path_arr[:, 1], 'r--')
            plt.pause(0.0001)

        for agent in self.entities():
            trail_arr = np.array(agent.trail)
            plt.plot(trail_arr[:, 0], trail_arr[:, 1])
            #plt.plot(self.trajectory_trail[:, 0], self.trajectory_trail[:, 1], 'r--')
            plt.plot(np.array(self.center_trail)[:, 0], np.array(self.center_trail)[:, 1], 'b-')
        plt.show()

    def animate_coppelia(self):
        client = RemoteAPIClient()
        sim = client.getObject('sim')
        sim.startSimulation()

        plane_handle = sim.createPrimitiveShape(sim.primitiveshape_plane, [500, 500, 0])  # piano 500x500
        # sim.setBoolParameter(sim.boolparam_floor_visible, False)  # Disabilita il piano a scacchi
        sim.setShapeColor(plane_handle, None, sim.colorcomponent_ambient_diffuse, [0.35, 0.55, 0.35])  # Colore verde
        sim.setObjectPosition(plane_handle, -1, [0, 0, 0.02])  # poco sotto origine
        
        point_path_list=[]
        last_five=[0.2, 0., 0., 0., 0.]
        for point in self.original_path:
            point_path_list.append(point[0])
            point_path_list.append(point[1])
            point_path_list.extend(last_five)
        #path_handle = sim.createPath(point_path_list, 2|4|8|16, 0, 0, 0, [0,0,1])
        #sim.setObjectPosition(path_handle, -1, [0, 0, 0.01])

        section=[0.02,-0.02,0.02,0.02,-0.02,0.02,-0.02,-0.02,0.02,-0.02]
        color=[0.,0.,1.]

        shape_handle=sim.generateShapeFromPath(point_path_list, section, 0, [0,0,1])
        sim.setShapeColor(shape_handle, None, sim.colorcomponent_ambient_diffuse, color)
        #path_handle = sim.createPath(self.center_trail, 2|4|8, 0, [1, 0, 0], [0, 0, 1], [1, 0, 0])
        #sim.setObjectPosition(path_handle, -1, [0, 0, 0.01])
        #path_handle=sim.generateShapeFromPath(self.center_trail)
        #sim.setObjectPosition(path_handle, -1, [0, 0, 0.01])

        dog_instances = []
        sheep_instances = []
        drones_instances = []

        for dog in self.dogs:
            # Crea una sfera e impostala nella posizione iniziale
            dog_handle = sim.createPrimitiveShape(sim.primitiveshape_spheroid, [0.4, 0.4, 0.4])
            sim.setShapeColor(dog_handle, None, sim.colorcomponent_ambient_diffuse, [0, 0, 0])  # Colore rosso
            dog_instances.append([dog, dog_handle])

        for sheep in self.sheeps:
            sheep_handle = sim.createPrimitiveShape(sim.primitiveshape_spheroid, [0.2, 0.2, 0.2])
            sim.setShapeColor(sheep_handle, None, sim.colorcomponent_ambient_diffuse, [1, 1, 1])
            sheep_instances.append([sheep, sheep_handle])

        for drone in self.drones:
                drone_handle = sim.createPrimitiveShape(sim.primitiveshape_spheroid, [0.4, 0.4, 0.4])
                sim.setShapeColor(drone_handle, None, sim.colorcomponent_ambient_diffuse, [1, 0, 0])
                drones_instances.append([drone, drone_handle])

        instances_list = dog_instances + sheep_instances + drones_instances

        for i in range(self.iter_steps_n - 1):
            for py_agent, copp_agent in instances_list:
                if isinstance(py_agent, Drone):
                    sim.setObjectPosition(copp_agent, -1, py_agent.trail[i].tolist() + [4])
                else:
                    sim.setObjectPosition(copp_agent, -1, py_agent.trail[i].tolist() + [0])
            #time.sleep(0.01)

        #sim.saveScene('scene.ttt')
        #sim.stopSimulation()

if __name__ == '__main__':
    a = Simulation()
    T = 1000.
    dt = 0.025
    tracking_speed=1.1
    points = [[-10, 10.], [0., 0.]]#, (-100, -200), (-50, -100), (0, -50), (50, 50), (100, 100), (150, 150), (200, 200)]
    points = [np.array(i) for i in points]
    a.add_dog([9.9-20, 0.4])
    a.add_dog([10.3-20, 0.5])
    a.add_dog([10.4-20, 0.6])
    a.add_dog([10-20, 0])
    a.add_dog([-10.1-20, 0.2])
    a.add_dog([-10-20, 0.3])
    a.initial_configurations(dt, tracking_speed)
    a.add_drones(5, initial_area= 5, center=a.center_trail[0])
    a.add_sheeps(20, 3)
    a.enter_path(points)

    #a.center_trail.clear()
    '''a.formation_control_on()
    a.compute_dog_center()
    a.add_sheeps(20, initial_area=5, center=a.center_trail[0])
    a.center_trail.pop(0)'''
    
    a.simulate(T, dt)

    #input("Press Enter to continue...")

    print("lost sheep:",len(a.lose_sheeps))
    #a.animate_coppelia()
    a.animate(grid_dimension=80)
