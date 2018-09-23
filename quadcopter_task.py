import numpy as np
from physics_sim import PhysicsSim

class Quadcopter_Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        print("sim.init_pos:{}".format(self.sim.init_pose))
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        #reward = 1.-.3*(abs(self.sim.pose[:3] - self.target_pos)).sum()
        # Compute reward / penalty and check if this episode is complete
        #done = False
        # reward = zero for matching target z, -ve as you go farther, upto -20
        #reward = -min(abs(self.target_pos[2] - self.sim.pose[2]), 20.0)  
        reward = np.tanh(1 - 0.003*(abs(self.sim.pose[:3] - self.target_pos))).sum()
        #print("reward:{}".format(reward))
        '''
        if self.sim.pose[2] >= self.target_pos[2]:  # agent has crossed the target height
            reward += 10.0  # bonus reward
            self.sim.done= True
        elif self.sim.time > self.sim.runtime:  # agent has run out of time
            reward -= 10.0  # extra penalty 
            self.sim.done= True
            '''
        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        done = False
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
            if done:
                reward += 10
        #reward = np.tanh(reward)
        next_state = np.concatenate(pose_all)
        #print("next_state:{}".format(next_state))
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state