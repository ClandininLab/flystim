#!/usr/bin/env python3

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from flystim.trajectory import RectangleTrajectory

from time import sleep
import numpy as np

def main():
    manager = launch_stim_server(Screen(fullscreen=False))

    update_rate = 10
    stixel_size = 5
    num_theta = 10
    num_phi = 6
    t_dim = 30
    background = 0.5
    
    center_theta = 90
    center_phi = 90
    
    encoding_scheme = 'single_spot'
    stimulus_code = np.random.choice(range(num_phi * num_theta), size = (1, t_dim)).flatten().tolist()

#    encoding_scheme = 'ternary_dense'
#    stimulus_code = np.random.rand(num_phi, num_theta, t_dim).flatten().tolist()
    

    manager.load_stim(name='MovingPatch', background = background, trajectory=RectangleTrajectory(w = 0, h = 0).to_dict())
    manager.load_stim('ArbitraryGrid', stixel_size = stixel_size, 
                      num_theta = num_theta, num_phi = num_phi, t_dim = t_dim, update_rate = update_rate, 
                      center_theta = center_theta, center_phi = center_phi, background = background, 
                      stimulus_code = stimulus_code, encoding_scheme = encoding_scheme, hold = True)
    sleep(1)

    manager.start_stim()
    sleep(3)

    manager.stop_stim()
    sleep(1)

if __name__ == '__main__':
    main()