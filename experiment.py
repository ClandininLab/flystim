#!/usr/bin/env python3
import multiprocessing
from flystim.stim_server import launch_stim_server 
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep

    
def get_subscreen(dir):
    # Define screen(s) for the rig. Units in meters
    # Fly is at (0, 0, 0), fly looking down +y axis.
    width = 1920
    height = 1080

    z_bottom  = - height/2
    z_top     = + height/2
    x_left    = - width/2
    x_right   = + width/2
    y_forward = + width/2
    y_back    = - width/2
    
    if dir == 'l':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left, y_back,    z_bottom)
        pb = (x_left, y_forward, z_bottom)
        pc = (x_left, y_back,    z_top)

    elif dir == 'c':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left,  y_forward, z_bottom)
        pb = (x_right, y_forward, z_bottom)
        pc = (x_left,  y_forward, z_top)

    elif dir == 'r':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_right, y_forward, z_bottom)
        pb = (x_right, y_back,    z_bottom)
        pc = (x_right, y_forward, z_top)

    elif dir == 'aux':
        viewport_ll = (-1.0, -1.0)
        viewport_width  = 2
        viewport_height = 2
        pa = (x_left,  y_forward, z_bottom)
        pb = (x_right, y_forward, z_bottom)
        pc = (x_left,  y_forward, z_top)

    else:
        raise ValueError('Invalid direction.')

    return SubScreen(pa=pa, pb=pb, pc=pc, viewport_ll=viewport_ll, viewport_width=viewport_width, viewport_height=viewport_height)

class Server():
    def __init__(self, screens=[]):
        self.manager = StimServer(screens=screens, host='', port=60629, auto_stop=False)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)

        def signal_handler(sig, frame):
            print('Closing server after Ctrl+C...')
            self.close()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)
        
        # self.manager.register_function_on_root(run_wn,'run_wn')

    def loop(self):
        self.manager.loop()

    def close(self):
        self.loco_manager.close()
        self.daq_device.close()
        self.manager.shutdown_flag.set()

    # def __set_up_loco__(self, loco_class, **kwargs):
        # self.loco_manager = loco_class(fs_manager=self.manager, start_at_init=False, **kwargs)
        # self.manager.register_function_on_root(self.loco_manager.set_save_directory, "loco_set_save_directory")
        # self.manager.register_function_on_root(self.loco_manager.start, "loco_start")
        # self.manager.register_function_on_root(self.loco_manager.close, "loco_close")
        # self.manager.register_function_on_root(self.loco_manager.set_pos_0, "loco_set_pos_0")
        # self.manager.register_function_on_root(self.loco_manager.write_to_log, "loco_write_to_log")
        # self.manager.register_function_on_root(self.loco_manager.loop_start, "loco_loop_start")
        # self.manager.register_function_on_root(self.loco_manager.loop_stop, "loco_loop_stop")
        # self.manager.register_function_on_root(self.loco_manager.loop_start_closed_loop, "loco_loop_start_closed_loop")
        # self.manager.register_function_on_root(self.loco_manager.loop_stop_closed_loop, "loco_loop_stop_closed_loop")
        # self.manager.register_function_on_root(self.loco_manager.loop_update_closed_loop_vars, "loco_loop_update_closed_loop_vars")
        # self.manager.register_function_on_root(self.loco_manager.sleep, "loco_sleep")
        # self.manager.register_function_on_root(self.loco_manager.update_pos, "loco_update_pos")
        # self.manager.register_function_on_root(self.loco_manager.update_pos_for, "loco_update_pos_for")

    # def __set_up_daq__(self, daq_class, **kwargs):
    #     self.daq_device = daq_class(**kwargs)
    #     self.manager.register_function_on_root(self.daq_device.sendTrigger, "daq_sendTrigger")
    #     sdelf.manager.register_function_on_root(self.daq_device.outputStep, "daq_outputStep")
def main():
    dur = 10#20*60 #30 minutes
    theta_vel = 250 #deg/s
    grating_rate = 50

    left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.03, 0.08), square_loc=(-1, -1), name='Left', horizontal_flip=False)

    center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.035, 0.08), square_loc=(-1, -1), name='Center', horizontal_flip=False)

    right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.04, 0.08), square_loc=(-1, +0.92), name='Right', horizontal_flip=False)

    #aux_screen = Screen(subscreens=[get_subscre n('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)
    screens = [left_screen, center_screen, right_screen]

    manager = launch_stim_server(screens)

    #manager.black_corner_square()
    manager.set_idle_background(0)

    from flystim.root_stimuli import natural_movie 
    memname = 'five'
    movie_thread  = multiprocessing.Process(target=natural_movie, args=(memname,'/home/baccuslab/stimulus_videos/forest_walk.mp4',))
    movie_thread.start()
    # print('what')
    sleep(5)
    manager.load_stim(name='PixMap', memname=memname)
    manager.start_stim()
    manager.set_global_theta_offset(270)
    # i = 0
    sleep(600)    #     manager.set_global_fly_pos(0,0,0)
    #     sleep(0)

    # manager.stop_stim(print_profile=True)
    # sleep(0.5)
    
    # manager.black_corner_square()
    # manager.set_idle_background(0)
if __name__ == '__main__':
    main()

