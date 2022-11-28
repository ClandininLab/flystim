#!/usr/bin/env python3
from flystim.root_stimuli import NaturalMovie, WhiteNoise
import flyrpc.multicall
import random_word
import cv2
import threading
import multiprocessing
from flystim.stim_server import launch_stim_server 
from flystim.screen import Screen, SubScreen
from flystim.trajectory import Trajectory
from math import pi, radians
import matplotlib.pyplot as plt
from flystim.draw import draw_screens

from time import sleep

def get_dim(fpath):
    cap = cv2.VideoCapture(fpath)
    r,f = cap.read()
    del cap
    return f.shape
    
def get_subscreen(dir):
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
        pc = (x_left,  y_back, z_top)

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

    left_screen = Screen(subscreens=[get_subscreen('l')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.07, 0.07), square_loc=(-1, -1), name='Left', horizontal_flip=False)
    center_screen = Screen(subscreens=[get_subscreen('c')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.07, 0.07), square_loc=(0.9, -1), name='Center', horizontal_flip=False)
    right_screen = Screen(subscreens=[get_subscreen('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.05, 0.05), square_loc=(0.95, -1), name='Right', horizontal_flip=False)
    aux_screen = Screen(subscreens=[get_subscreen('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)
    screens = [left_screen, center_screen, right_screen]

    manager = launch_stim_server(screens)
    manager = flyrpc.multicall.MyMultiCall(manager)

    manager.black_corner_square()
    manager.set_idle_background(0)
    manager()
    
    sleep(10)

    random_word_generator = random_word.RandomWords()
    MEMNAME = random_word_generator.get_random_word()
    wn = WhiteNoise(MEMNAME, (70,270), 100)
    threading.Thread(target=wn.stream).start()
    sleep(5)
    manager.start_corner_square()
    manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=(70,270,3))
    manager.start_stim()
    manager()

    sleep(20)

    manager.stop_stim()
    manager.set_idle_background(0)
    manager.black_corner_square()
    manager()


        

    fpath = '/home/baccuslab/Videos/stimulus_videos/baker.avi'
    random_word_generator = random_word.RandomWords()
    MEMNAME = random_word_generator.get_random_word()
    dim = get_dim(fpath)
    nm = NaturalMovie(MEMNAME, fpath, 70)
    nm.warmup(3000)
    threading.Thread(target=nm.stream).start()
    sleep(20)

    manager.start_corner_square()
    manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=dim)
    manager.start_stim()
    manager()

    sleep(20*60)    #     manager.set_global_fly_pos(0,0,0)
    nm.saveout()
    nm.close()

    manager.stop_stim()
    manager.set_idle_background(0)
    manager.black_corner_square()
    manager()

    # random_word_generator = random_word.RandomWords()
    # MEMNAME = random_word_generator.get_random_word()
    
    # fpath = '/home/baccuslab/Videos/stimulus_videos/baker.avi'
    # dim = get_dim(fpath)
    # nm = NaturalMovie(MEMNAME, fpath, 70)
    # nm.warmup(2000)
    # threading.Thread(target=nm.stream).start()
    # sleep(2)
    # manager.start_corner_square()
    # manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=dim)
    # manager.start_stim()

    # sleep(20)    #     manager.set_global_fly_pos(0,0,0)
    # # nm.close()

    # nm.saveout()

    # manager.stop_stim()
    # manager.set_idle_background(0)

    # random_word_generator = random_word.RandomWords()
    # MEMNAME = random_word_generator.get_random_word()
    
    # nm = WhiteNoise(MEMNAME, (70,270), 100)
    # threading.Thread(target=nm.stream).start()
    # sleep(5)

    # manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=((70,270,3)))
    # manager.start_stim()

    # sleep(60*10)    #     manager.set_global_fly_pos(0,0,0)
    # manager.stop_stim()
    # manager.set_idle_background(0)
    
    # random_word_generator = random_word.RandomWords()
    # MEMNAME = random_word_generator.get_random_word()
    
    # fpath = '/home/baccuslab/Videos/stimulus_videos/baker.avi'
    # dim = get_dim(fpath)
    # nm = NaturalMovie(MEMNAME, fpath, 70)
    # nm.warmup(3000)
    # threading.Thread(target=nm.stream).start()
    # sleep(5)

    # manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=dim)
    # manager.start_stim()

    # sleep(60*10)    #     manager.set_global_fly_pos(0,0,0)
    # # nm.close()

    # manager.stop_stim()
    # manager.set_idle_background(0)
    # random_word_generator = random_word.RandomWords()
    # MEMNAME = random_word_generator.get_random_word()
    
    # nm = WhiteNoise(MEMNAME, (70,270), 100)
    # threading.Thread(target=nm.stream).start()
    # sleep(5)

    # manager.load_stim(name='PixMap', memname=MEMNAME, frame_size=((70,270,3)))
    # manager.start_stim()

    # sleep(60*10)    #     manager.set_global_fly_pos(0,0,0)
    # manager.stop_stim()
    # manager.set_idle_background(0)
    
    # # manager.black_corner_square()
    # manager.set_idle_background(0)
if __name__ == '__main__':
    main()

