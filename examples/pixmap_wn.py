#!/usr/bin/env python3
from flystim.stim_server import launch_stim_server
from flystim.screen import Screen
from time import sleep
import random_word


def main():

    memname = random_word.RandomWords().get_random_word()
    frame_shape = (200, 100, 3)
    nominal_frame_rate = 1
    duration = 4
    seed = 37

    manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))
    # manager = init_screens()

    manager.load_shared_pixmap_stim(name='WhiteNoise', memname=memname, 
                                    frame_shape=frame_shape, nominal_frame_rate=nominal_frame_rate, 
                                    dur=duration, seed=seed, coverage='full')


    manager.load_stim(name='PixMap', memname=memname, frame_size=frame_shape, rgb_texture=True, 
                        width=180, radius=1, n_steps=32, surface='spherical', hold=True)

    sleep(1)
    manager.start_shared_pixmap_stim()

    manager.start_stim()
    sleep(duration)

    manager.stop_stim(print_profile=True)
    manager.clear_shared_pixmap_stim()
    sleep(1)

    

if __name__ == '__main__':
    main()
