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
    def __init__(self, memname, frame_shape, nominal_frame_rate, dur, seed=37, logfile=None, coverage='full'):
        super().__init__(memname = memname)

        if logfile is None:
            input('Must provide a log filepath...')
        else:
            self.logfile = logfile
        self.coverage=coverage
        self.nominal_frame_rate = nominal_frame_rate
        self.dur = dur
        self.seed = seed
        dummy = np.zeros((frame_shape[0], frame_shape[1], 3))*255
        dummy = dummy.astype(np.uint8)
        
        self.reserve_memblock(dummy)

        with open(self.logfile,'a') as f: f.write('whitenoise - framerate: {} duration: {} seed: {}\n'.format(nominal_frame_rate, dur, seed))

        
    def stream(self):
        import sched
        s = sched.scheduler(time.time, time.sleep)
        begin_time = None

        def writetime(t, current_seed, pix0, pix01, pix10):
            with open(self.logfile, 'a') as f:
                f.write(f'{t} {current_seed} {pix0} {pix01} {pix10} \n')

        def genframe():
            t = time.time()-self.t
            seed = int(round(self.seed + t*self.nominal_frame_rate))
            np.random.seed(seed)
            img = np.random.rand(self.frame_shape[0], self.frame_shape[1])

            img_int = img*255/1.5+15
            img_int = img_int.astype(np.uint8)
                
            if self.coverage=='left':
                img_int[:,:int(img_int.shape[1]/2)] = 0
            self.global_frame[:,:,0] = img_int
            self.global_frame[:,:,1] = img_int
            self.global_frame[:,:,2] = img_int

            writetime(time.time(), seed, img[0,0], img[0,1], img[1,0])

        
        tis = np.arange(0,self.dur,1/self.nominal_frame_rate)
        tis = tis[1:]
        for ti in tis: 
            s.enter(ti, 1, genframe)

        run = False
        while not run:
            if self.global_frame[0,0,0] == 1:
                run = True
        self.t = time.time()
        s.run()



class NaturalMovie(RootStimulus):
    def __init__(self, memname, movie_path, nominal_frame_rate, dur, logfile):
        if logfile is None:
            input('Must provide a log filepath...')
        else:
            self.logfile = logfile

        super().__init__(memname = memname)
        self.nominal_frame_rate = nominal_frame_rate
        self.movie_path = movie_path
        self.dur = dur

        cap = CamGear(source=movie_path).start()

        frame = cap.read().astype(np.uint8)[:,:,:]


        self.reserve_memblock(frame)

        del cap
        with open(self.logfile, 'a') as f:
            f.write('naturalmovie - framerate: {} duration: {} file: {}\n'.format(nominal_frame_rate, dur, movie_path))


    def stream(self):
        import sched
        s = sched.scheduler(time.time, time.sleep)
        cap = CamGear(source=self.movie_path).start()
        
        def writetime(t,fr):
            with open(self.logfile,'a') as f:
                f.write(f'{t} {fr} \n')

        def genframe():
            img = cap.read()[:,:,:]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.uint8)
            self.global_frame[:,:,:] =  img

            fr = cap.stream.get(cv2.CAP_PROP_POS_FRAMES)
            writetime(time.time(), fr)

        tis = np.arange(0,self.dur,1/self.nominal_frame_rate)
        tis = tis[1:]
        for ti in tis: 
            s.enter(ti, 1, genframe)

        run = False
        while not run:
            if self.global_frame[0,0,0] == 1:
                run = True
        
        s.run()


