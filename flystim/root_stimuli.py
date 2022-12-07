import numpy as np
from multiprocessing import shared_memory
from vidgear.gears import CamGear
import cv2
import atexit
import time

class RootStimulus:
    def __init__(self, memname, shape=None):
        self.memname = memname
        if shape is not None:
            print('Reserved memory')
            dummy = np.ones(shape)
            self.reserve_memblock(dummy)
        else:
            print('Root stimulus initialized, waiting for frame')

    def reserve_memblock(self,frame):
        self.frame_shape = frame.shape
        self.frame_bytes = frame.nbytes
        self.frame_dtype = frame.dtype

        self.memblock = shared_memory.SharedMemory(create=True,size=self.frame_bytes,name=self.memname)
        atexit.register(self.close)
        self.global_frame = np.ndarray(self.frame_shape, dtype = self.frame_dtype, buffer=self.memblock.buf)
        self.global_frame[:] = np.zeros(self.frame_shape)

    def close(self):
        self.memblock.close()
        self.memblock.unlink()

class WhiteNoise(RootStimulus):
    def __init__(self, memname, frame_shape, nominal_frame_rate, dur, seed=37):
        super().__init__(memname = memname)
        self.nominal_frame_rate = nominal_frame_rate
        self.dur = dur
        self.seed = seed
        dummy = np.zeros((frame_shape[0], frame_shape[1], 3))*255
        dummy = dummy.astype(np.uint8)
        
        self.reserve_memblock(dummy)

        with open('/home/baccuslab/log.txt','a') as f:
            f.write('whitenoise')

        
    def stream(self):
        import sched
        s = sched.scheduler(time.time, time.sleep)
        begin_time = None

        def writetime(t):
            with open('/home/baccuslab/log.txt','a') as f:
                f.write(f'{t} \n')

        def genframe():
            t = time.time()-self.t
            seed = int(round(self.seed + t*self.nominal_frame_rate))
            np.random.seed(seed)
            img = np.random.rand(self.frame_shape[0], self.frame_shape[1])*255
            img = img.astype(np.uint8)
            self.global_frame[:,:,0] = img
            self.global_frame[:,:,1] = img
            self.global_frame[:,:,2] = img

            writetime(time.time())

        
        for ti in np.arange(0,self.dur,1/self.nominal_frame_rate):
            s.enter(ti, 1, genframe)

        run = False
        while not run:
            if self.global_frame[0,0,0] == 1:
                run = True
        self.t = time.time()
        s.run()
                # self.start_time = time.time()
                # while True:
                #     s.enter(1/self.nominal_frame_rate, 1, genframe)
                #     s.run()
                 





class NaturalMovie(RootStimulus):
    def __init__(self, memname, movie_path, nominal_frame_rate, dur):
        super().__init__(memname = memname)
        self.nominal_frame_rate = nominal_frame_rate
        self.movie_path = movie_path
        self.dur = dur

        cap = CamGear(source=movie_path).start()

        frame = cap.read().astype(np.uint8)
        self.reserve_memblock(frame)

        del cap
        with open('/home/baccuslab/log.txt','a') as f:
            f.write('naturalmovie')


    def stream(self):
        import sched
        s = sched.scheduler(time.time, time.sleep)
        cap = CamGear(source=self.movie_path).start()
        
        def writetime(t,fr):
            with open('/home/baccuslab/log.txt','a') as f:
                f.write(f'{t} {fr} \n')

        def genframe():
            img = cap.read()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.uint8)
            self.global_frame[:,:,:] =  img

            fr = cap.stream.get(cv2.CAP_PROP_POS_FRAMES)
            writetime(time.time(), fr)

            
        for ti in np.arange(0,self.dur,1/self.nominal_frame_rate):
            s.enter(ti, 1, genframe)
        run = False
        while not run:
            if self.global_frame[0,0,0] == 1:
                run = True
        
        s.run()

    def saveout(self):
        np.save('/home/baccuslab/{}_frs.npy'.format(self.memname), np.array(self.frs))
        np.save('/home/baccuslab/{}_ts.npy'.format(self.memname), np.array(self.ts))

