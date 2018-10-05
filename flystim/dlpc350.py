# ref: https://github.com/SivyerLab/pyCrafter4500

import platform
import time
import hid
from math import floor

def make_dlpc350_objects():
    """
    Returns a list of DLPC350 objects corresponding to the connected Lightcrafter 4500 units.
    """

    dlpc350_objects = []

    for d in hid.enumerate():
        if d['product_string'] != 'DLPC350':
            continue

        if platform.system() == 'Windows':
            if d['usage'] != 65280:
                continue
            if d['usage_page'] != 65280:
                continue
        elif platform.system() == 'Linux':
            path = d['path'].decode('utf-8')
            if path[-2:] != '00':
                continue

        device = hid.device()
        device.open_path(d['path'])
        dlpc350_objects.append(DLPC350(device=device))

    return dlpc350_objects

class DLPC350:
    def __init__(self, device, timeout=10, poll_period=0.1):
        """
        :param device: HIDAPI device corresponding to the Lightcrafter unit
        :param timeout: Time to wait (in seconds) when polling a register status
        :param poll_period: Delay (in seconds) between polls of a register status
        """

        # save settings
        self.device = device
        self.timeout = timeout
        self.poll_period = poll_period

    def command(self, mode, cmd2, cmd3, data=None):
        # set defaults
        if data is None:
            data = []

        # build up command
        command = []

        command.append(0)               # report ID = 0
        command.append(mode)            # read/write
        command.append(0)               # sequence number = 0
        command.append(2+len(data))     # length LSB
        command.append(0)               # length MSB
        command.append(cmd3)            # CMD3
        command.append(cmd2)            # CMD2
        command.extend(data)            # data

        # add padding
        command.extend([0]*(65-len(command)))

        # run command
        self.device.write(command)

    def write(self, cmd2, cmd3, data=None):
        # send command
        self.command(mode=0x40, cmd2=cmd2, cmd3=cmd3, data=data)

        # read response
        resp = self.device.read(64)

        # check response
        assert resp[0] == 0x40
        assert resp[1] == 0
        assert resp[4] == cmd3
        assert resp[5] == cmd2

    def read(self, cmd2, cmd3):
        # send command
        resp = self.command(mode=0xC0, cmd2=cmd2, cmd3=cmd3)

        # read response
        resp = self.device.read(64)

        # check response
        assert resp[0] == 0xC0
        assert resp[1] == 0

        # return data
        bytes = resp[2]
        return resp[4:(4+bytes)]

    def play_sequence(self):
        self.write(cmd2=0x1a, cmd3=0x24, data=[0x02])

    def stop_sequence(self):
        # write the state
        self.write(cmd2=0x1a, cmd3=0x24, data=[0x00])

        # poll the sequence state register
        start_time = time.time()
        while (time.time() - start_time) < self.timeout:
            resp = self.read(cmd2=0x1a, cmd3=0x24)[0]

            if resp == 0x00:
                break
            else:
                time.sleep(self.poll_period)
                continue
        else:
            raise Exception('Timed out waiting for sequence to stop.')

    def validate(self, allow_post_vector_warning=True):
        # start validation
        self.write(cmd2=0x1a, cmd3=0x1a, data=[0x00])

        # poll the validation register
        start_time = time.time()
        while (time.time() - start_time) < self.timeout:
            resp = self.read(cmd2=0x1a, cmd3=0x1a)[0]

            if ((resp >> 7) & 1) == 1:
                # if bit 7 is set, it means that validation is still ongoing
                time.sleep(self.poll_period)
                continue
            elif resp == 0:
                # "0" means no errors
                break
            elif (resp == 8) and allow_post_vector_warning:
                # "8" means that a post vector was not inserted.  But that's expected when there is no
                # black period following a pattern.
                break
            else:
                raise Exception('Invalid configuration')
        else:
            raise Exception('Timed out waiting for pattern sequence validation.')

    def pattern_mode(self, fps=60):
        # stop sequence mode
        self.stop_sequence()

        # set display to pattern mode
        self.write(cmd2=0x1a, cmd3=0x1b, data=[0x01])

        # pattern data streamed over video
        self.write(cmd2=0x1a, cmd3=0x22, data=[0x00])

        # pattern LUT
        # 0x00 = One entry
        # 0x01 = Always repeat the pattern sequence, once a sequence is completed
        # 0x00 = Display 1 pattern
        # 0x00 = unused with streaming input
        self.write(cmd2=0x1a, cmd3=0x31, data=[0x00, 0x01, 0x00, 0x00])

        # select VSYNC as trigger source
        self.write(cmd2=0x1a, cmd3=0x23, data=[0x00])

        # write period/exposure
        period_us = int(floor(1e6/fps))
        time_data = [(period_us >> shift) & 0xff for shift in [0, 8, 16, 24]]
        self.write(cmd2=0x1a, cmd3=0x29, data=(time_data+time_data))

        # open mailbox
        self.write(cmd2=0x1a, cmd3=0x33, data=[0x02])

        # set mailbox offset
        self.write(cmd2=0x1a, cmd3=0x32, data=[0x00])

        # write LUT data
        # 0x09 == use 8 bits blue data, with external positive trigger
        # 0x48 == blue LED, with 8 bit color depth
        # 0x04 == trigger out 1 frames pattern, perform buffer swap, do not insert post pattern, do not invert pattern
        self.write(cmd2=0x1a, cmd3=0x34, data=[0x09, 0x48, 0x04])

        # close mailbox
        self.write(cmd2=0x1a, cmd3=0x33, data=[0x00])

        # run validation
        self.validate()

        # start pattern mode
        self.play_sequence()
        time.sleep(0.1)
        self.play_sequence()
