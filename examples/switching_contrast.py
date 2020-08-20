#!/usr/bin/env python3

# Example client program that randomly cycles through different rotation rates.
# The stim_type can be either SineGrating or RotatingBars.

from time import sleep
from random import choice
import itertools
import numpy as np

from flystim.stim_server import launch_stim_server
from flystim.screen import Screen

def main():

    n_repeats = 1

    iti = 5
    iti_color = 0.5
    temporal_frequency = 1 #Hz
    spatial_frequency = 60 #degrees
    rate = temporal_frequency * spatial_frequency

    high_max_lum = 1
    high_min_lum = 0
    low_max_lum = 0.625
    low_min_lum = 0.375
    signs = [-1, 1]
    high_contrast_firsts = [False, True]
    trial_types = list(itertools.product(signs, high_contrast_firsts))
    n_trial_types = len(trial_types)
    trial_sample_idxes = np.random.permutation(np.repeat(np.arange(n_trial_types), n_repeats))
    n_trials = n_trial_types * n_repeats

    #screen = Screen(server_number=1, id=1,fullscreen=True, tri_list=make_tri_list(), vsync=False, square_side=0.01, square_loc=(0.59,0.74))
    screen = Screen(fullscreen=False, vsync=False)
    manager = launch_stim_server(screen)
    manager.set_idle_background(iti_color)
    for i in range(n_trials):
        sleep(iti)
        sign, high_contrast_first = trial_types[trial_sample_idxes[i]]
        signed_rate = sign*rate
        if high_contrast_first:
            max_lum_1,min_lum_1 = high_max_lum,high_min_lum
            max_lum_2,min_lum_2 = low_max_lum,low_min_lum
        else:
            max_lum_1,min_lum_1 = low_max_lum,low_min_lum
            max_lum_2,min_lum_2 = high_max_lum,high_min_lum

        manager.load_stim(name='SineGrating', period=spatial_frequency, rate=sign*rate, color=max_lum_1, background=min_lum_1, angle=0, offset=0)
        manager.start_stim()
        sleep(5)
        manager.update_stim(color=max_lum_2, background=min_lum_2)
        sleep(5)
        manager.stop_stim()


if __name__ == '__main__':
    main()
