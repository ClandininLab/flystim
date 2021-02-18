import logging
import socket
from time import time

FT_FRAME_NUM_IDX = 0
FT_THETA_IDX = 16
FT_TIMESTAMP_IDX = 21
FT_SQURE_IDX = 25
FICTRAC_HOST = '127.0.0.1'  # The server's hostname or IP address
FICTRAC_PORT = 33334         # The port used by the server
FICTRAC_BIN =    "/home/clandinin/lib/fictrac211/bin/fictrac"
FICTRAC_CONFIG = "/home/clandinin/lib/fictrac211/config_MC.txt"

class FtManager():
    def __init__(self, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG):
        self.p = subprocess.Popen([FICTRAC_BIN, FICTRAC_CONFIG, "-v","ERR"], start_new_session=True)
        self.ft_buffer = ""
        sleep(2)

    def close(self):
        self.p.kill()
        self.p.terminate()

    def sleep(self, duration):
        sleep(duration)


class FtSocketManager():
    def __init__(self, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT):
        self.ft_manager = FtManager(ft_bin=ft_bin, ft_config=ft_config)

        self.ft_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ft_sock.bind((ft_host, ft_port))
        self.ft_sock.setblocking(0)

    def sleep(self, duration):
        t_start = time()
        while time()-t_start < duration:
            _ = self.get_data()

    def close(self):
        self.ft_sock.close()
        self.ft_manager.close()

    def get_data(self, ft_data_idx=[FT_THETA_IDX]):

        # if not select.select([sock], [], [])[0]:
        #     return fictrac_get_data(sock)
        ready = select.select([self.ft_sock], [], [])[0]
        if ready:
            data = self.ft_sock.recv(4098)
        else:
            return self.get_data()

        # Decode received data
        ogline = data.decode('UTF-8')
        line = self.ft_buffer + ogline
        endline = line.rfind("\n")
        if endline == -1: # there is no linebreak
            startline = line.rfind("FT")
            if startline != -1: #there is line start
                line = line[startline:]
            self.ft_buffer += line # add (perhaps) trimmed line to buffer
            logging.warning("No line end: %s", line)
            return self.get_data()
        else: # there is a linebreak
            self.ft_buffer = line[endline:] # write everything after linebreak to the buffer
            line = line[:endline]
            startline = line.rfind("FT")
            if startline == -1: #there is no line start... this shouldn't happen bc we have a buffer
                logging.warning("No line start: %s", line)
                return self.get_data()
            else: # start line exists as well as a linebreak, so trim to the start
                line = line[startline:]

        # There is a complete line!
        toks = line.split(", ")

        if len(toks) != 27:
            logging.warning("This should not happen: %s", str(len(toks)) + ' ' + line)
            return self.get_data()

        frame_num = int(toks[FT_FRAME_NUM_IDX+1])
        ts = float(toks[FT_TIMESTAMP_IDX+1])
        data = [float(toks[i+1]) for i in ft_data_idx]

        return frame_num, ts, data

class FtClosedLoopManager():
    def __init__(self, fs_manager, ft_bin=FICTRAC_BIN, ft_config=FICTRAC_CONFIG, ft_host=FICTRAC_HOST, ft_port=FICTRAC_PORT):
        self.ft_socket = FtSocketManager(ft_bin=ft_bin, ft_config=ft_config, ft_host=ft_host, ft_port=ft_port)
        self.fs_manager = fs_manager

        self.theta_0 = None #radians

    def sleep(self, duration):
        t_start = time()
        while time()-t_start < duration:
            _ = self.ft_socket.get_data()

    def close(self):
        self.ft_socket.close()

    def set_theta_0(self, theta_0=None): #radians
        self.fs_manager.set_global_theta_offset(0)
        if theta_0 is None:
            _, _, data = self.ft_socket.get_data(ft_data_idx=[FT_THETA_IDX])
            self.theta_0 = data[0]
        else:
            self.theta_0 = theta_0

    def update_theta(self):
        frame_num, ts, data = self.ft_socket.get_data(ft_data_idx=[FT_THETA_IDX])
        theta_1 = data[0]
        theta = theta_1 - self.theta_0 if self.theta_0 is not None else 0
        self.fs_manager.set_global_theta_offset(degrees(theta))
        return frame_num, ts, theta

    def update_theta_for(self, duration):
        t_start = time()
        while time()-t_start < duration:
            _ = self.update_theta()
