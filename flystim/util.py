from math import sin, cos
from numbers import Number
import numpy as np
import os, sys
import inspect
import importlib
import importlib.resources
import random
import string
import warnings
import flystim
from .trajectory import Trajectory

def load_stim_module_paths_from_file():
    path_for_paths_to_other_stimuli = importlib.resources.files(flystim).joinpath('paths_to_other_stimuli.txt')
    if not os.path.exists(path_for_paths_to_other_stimuli):
        print('No paths_to_other_stimuli.txt found!')
        print('Creating new file at paths_to_other_stimuli - please fill this in with paths (one per line) of files with any other stimuli you want to use.')
        with open(path_for_paths_to_other_stimuli, "w") as text_file:
            text_file.write('/path/to/other/stimuli')

    with open(path_for_paths_to_other_stimuli, "r") as paths_file:
        other_stim_module_paths = [x for x in paths_file.readlines() if os.path.exists(x.strip())]
        
    return other_stim_module_paths

def load_stim_module_from_path(path, module_name='loaded_module', submodules=['stimuli', 'trajectory', 'distribution']):
    '''
    Load a module from specified path. Module must contained specified submodules.
    '''
    for submodule_name in submodules:
        submodule_name_full = module_name+'.'+submodule_name
        submodule_path = os.path.join(path, submodule_name+'.py')
        if not os.path.exists(submodule_path):
            warnings.warn(f'Could not find {submodule_name} at {submodule_path}')
            continue
        spec = importlib.util.spec_from_file_location(submodule_name_full, submodule_path)
        loaded_mod = importlib.util.module_from_spec(spec)
        sys.modules[submodule_name_full] = loaded_mod
        spec.loader.exec_module(loaded_mod)
    return

def generate_lowercase_barcode(length=5, existing_barcodes=[]):
    """Generates a random barcode that is not in existing_barcodes"""
    barcode = ''.join(random.choice(string.ascii_lowercase) for i in range(length))
    while barcode in existing_barcodes:
        barcode = ''.join(random.choice(string.ascii_lowercase) for i in range(length))
    return barcode

def get_all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in get_all_subclasses(c)])

def make_as(parameter, parent_class=Trajectory):
    """Return parameter as parent class object if it is a dictionary."""
    if type(parameter) is dict: # trajectory-specifying dict
        subclasses = get_all_subclasses(parent_class)
        subclass_names = [sc.__name__ for sc in subclasses]
        
        assert parameter['name'] in subclass_names, f'Unrecognized subclass name {parameter["name"]} for parent class {parent_class.__name__}.'
        
        subclass_candidates = [sc for sc in subclasses if sc.__name__ == parameter['name']]
        if len(subclass_candidates) > 1:
            print(f'Multiple subclasses with name {parameter["name"]} for parent class {parent_class.__name__}.')
            print(f'Choosing the last one: {subclass_candidates[-1]}')
        
        chosen_subclass = subclass_candidates[-1]
        
        # check that all required arguments are specified
        traj_params = inspect.signature(chosen_subclass.__init__).parameters.values()
        for p in traj_params:
            if p.name != 'self' and p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty:
                assert p.name in parameter, f'Required subclass parameter {p.name} not specified.'
        
        # remove name parameter
        parameter.pop('name')
        
        return chosen_subclass(**parameter)
    
    else: # not specified as a dict, just return the original param
        return parameter

def listify(x, type_):
    if isinstance(x, (list, tuple)):
        return x

    if isinstance(x, type_):
        return [x]

    raise ValueError('Unknown input type: {}'.format(type(x)))

def normalize(vec):
    return vec / np.linalg.norm(vec)

# rotation matrix reference:
# https://en.wikipedia.org/wiki/Rotation_matrix

def rotate(pts, yaw, pitch, roll):
    """
    :param yaw: rotation around z axis, radians
    :param pitch: rotation around x axis, radians
    :param roll: rotation around y axis, radians
    """
    R = rot_mat(yaw, pitch, roll)
    return R @ pts

def rot_mat(yaw, pitch, roll):
    """
    :param yaw: rotation around z axis, radians
    :param pitch: rotation around x axis, radians
    :param roll: rotation around y axis, radians
    """
    return rotz_mat(yaw) @ rotx_mat(pitch) @ roty_mat(roll)

def rotx(pts, th):
    return rotx_mat(th).dot(pts)

def rotx_mat(th):
    return np.array([[1,       0,         0],
                     [0, +cos(th), -sin(th)],
                     [0, +sin(th), +cos(th)]], dtype=float)

def roty(pts, th):
    return roty_mat(th).dot(pts)

def roty_mat(th):
    return np.array([[+cos(th), 0, +sin(th)],
                     [0,        1,        0],
                     [-sin(th), 0, +cos(th)]], dtype=float)

def rotz(pts, th):
    return rotz_mat(th).dot(pts)

def rotz_mat(th):
    return np.array([[+cos(th), -sin(th), 0],
                     [+sin(th), +cos(th), 0],
                     [       0,        0, 1]], dtype=float)

def scale(pts, amt):
    return np.multiply(amt, pts)

def spherical_to_cartesian(r, theta, phi):
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return x, y, z

def cartesian_to_spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y, z)
    phi = np.arccos(z/r) # np.arctan2(np.sqrt(x**2 + y**2), z)
    return r, theta, phi

def cylindrical_to_cartesian(r, theta, z):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = z
    return x, y, z

def cartesian_to_cylindrical(x, y, z):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    z = z
    return r, theta, z

def cylindrical_w_phi_to_cartesian(r, theta, phi):
    '''
    Converts cylindrical coordinates with phi instead of z (r, theta, phi) to cartesian coordinates
    '''
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = r / np.tan(phi)
    return x, y, z

def cartesian_to_cylindrical_w_phi(x, y, z):
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    phi = np.arctan2(z, r)
    return r, theta, phi

def translate(pts, amt):
    # convert point(s) and translate amount to numpy arrays
    pts = np.array(pts, dtype=float)
    amt = np.array(amt, dtype=float)

    # add offset in a manner that depends on whether the input is 1D or 2D
    if len(pts.shape) == 1:
        return pts + amt
    elif len(pts.shape) == 2:
        return pts + amt[:, np.newaxis]

def get_rgba(val, def_alpha=1):
    # interpret string as RGB
    if isinstance(val, str):
        if val.lower() == 'red':
            val = (1, 0, 0)
        elif val.lower() == 'green':
            val = (0, 1, 0)
        elif val.lower() == 'blue':
            val = (0, 0, 1)
        elif val.lower() == 'yellow':
            val = (1, 1, 0)
        elif val.lower() == 'magenta':
            val = (1, 0, 1)
        elif val.lower() == 'cyan':
            val = (0, 1, 1)
        elif val.lower() == 'white':
            val = (1, 1, 1)
        elif val.lower() == 'black':
            val = (0, 0, 0)
        else:
            raise ValueError(f'Unknown color: {val}')

    # if a single number is given treat as monochrome
    if isinstance(val, Number):
        return (val, val, val, def_alpha)

    # otherwise if three numbers are given add the default alpha
    if len(val) == 3:
        return (val[0], val[1], val[2], def_alpha)
    elif len(val) == 4:
        return val
    else:
        raise ValueError(f'Cannot use value with length {len(val)}.')
