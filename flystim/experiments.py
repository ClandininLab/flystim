from flystim.screen import Screen, SubScreen
from flystim.stim_server import launch_stim_server 
import flyrpc.multicall
import cv2

def init_screens():
    left_screen = Screen(subscreens=[get_subscreens('l')], server_number=1, id=2, fullscreen=True, vsync=True, square_size=(0.1, 0.1), square_loc=(-1, -1), name='Left', horizontal_flip=False)
    center_screen = Screen(subscreens=[get_subscreens('c')], server_number=1, id=1, fullscreen=True, vsync=True, square_size=(0.1, 0.1), square_loc=(0.9, -1), name='Center', horizontal_flip=False)
    right_screen = Screen(subscreens=[get_subscreens('r')], server_number=1, id=3, fullscreen=True, vsync=True, square_size=(0.1, 0.1), square_loc=(0.9, -1), name='Right', horizontal_flip=False)
    aux_screen = Screen(subscreens=[get_subscreens('aux')], server_number=1, id=0, fullscreen=False, vsync=True, square_size=(0, 0), square_loc=(-1, -1), name='Aux', horizontal_flip=False)

    screens = [left_screen, center_screen, right_screen]

    manager = flyrpc.multicall.MyMultiCall(launch_stim_server(screens))

    return manager

def get_subscreens(dir):
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

def get_video_dim(fileapth):
    cap = cv2.VideoCapture(fileapth)
    ret = False
    while not ret:
        ret, frame = cap.read()
    return frame.shape
