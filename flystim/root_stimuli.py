import numpy as np
from multiprocessing import shared_memory
from vidgear.gears import CamGear
import atexit
import time

def close(shm):
    shm.close()
    shm.unlink()

def natural_movie(memname, fpath):
    CG = CamGear(source=fpath).start()
    img = CG.read()
    a = img


    shm = shared_memory.SharedMemory(create=True,size=a.nbytes,name=memname)
    atexit.register(close,shm=shm)
    b = np.ndarray(a.shape, dtype=a.dtype, buffer=shm.buf)
    b[:] = np.zeros(a.shape)

    # Warmup
    for i in range(60*20): 
        print(i)
        CG.read()

    print('Finished seeking')

    while True:
        if b[0,0,0] == 1:
            print('running')
            while True:
                try:
                    img = CG.read()
                except:
                    pass
                b[:] =  img
                time.sleep(1/100)



