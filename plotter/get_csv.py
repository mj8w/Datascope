# -*- coding: utf-8 -*-
"""
Get csv formatted data from serial port and buffer for plotting
"""
from serial import Serial, SerialException

from data_thread import DataThread

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

debug, info, warn, err = logset('data')

class CSV_Buffer(DataThread):
    """ Receives csv formatted data and interprets it into data
        points to be further processed and graphed.
    """

    def __init__(self, comport):
        super().__init__()

        self.comport = comport
        self.source = None
        self.max_signal_count = config["max_signal_count"]

    def open(self):
        try:
            self.source = Serial(self.comport, baudrate = 115200, timeout = 0.05) # timeout set for visual continuity on graph
        except SerialException:
            return False
        return True

    def run(self):
        """ Class Thread override - the thread to run """
        self.quit = False
        debug("start run()")
        while 1:
            try:
                abyte = self.source.read(1)
            except SerialException:
                if self.quit:
                    break
                continue

            msg = [abyte]
            tstamp = self.timestamp() # time starts with first byte received

            while 1:
                try:
                    abyte = self.source.read(1)
                except SerialException:
                    if self.quit:
                        break
                    continue

                msg.append(abyte)
                if abyte == b'\n':
                    break

            if self.quit:
                break

            # received end of line - what we need for a packet
            try:
                line = "".join([a.decode('utf-8') for a in msg])
            except UnicodeDecodeError:
                continue # abort this line - it is invalid

            line = line.strip(" \r\n")
            try:
                data = [float(x) for x in line.split(',')]
                data = data[:self.max_signal_count] # limit data to just what system is capable of.
                valid_bitmask = (1 << len(data)) - 1 # mark all bits '1' for signals that are valid in the packet

                # compose a packet and buffer it up
                self.queue.put((tstamp, valid_bitmask, data))
                self.save_csv_entry((tstamp, valid_bitmask, data))        # save entry in case we save the plot data to file later
                
                debug("{:3.4f} {} {!r}".format(tstamp, valid_bitmask, data))
            except ValueError:
                debug("*** line='{}' Failed to parse... ***".format(line))
                pass
