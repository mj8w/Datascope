# -*- coding: utf-8 -*-
"""
Get csv formatted data from serial port and buffer for plotting
"""

from queue import Queue
from threading import Thread
from time import time

from serial import Serial, SerialException

from config import logset, max_signal_count

debug, info, warn, err = logset('decomp')

class CSV_Buffer(Thread):
    """ Receives csv formatted data and interprets it into data
        points to be further processed and graphed.
    """

    def __init__(self, comport):
        super().__init__()

        self.comport = comport

        # queue to store data collected from the serial port
        self.queue = Queue()

        # set the timestamp
        self.start_time = time()

        # start reading the serial port
        self.source = None
        self.quit = False
        self.daemon = True

    def open(self):
        try:
            self.source = Serial(self.comport, baudrate = 115200, timeout = 0.05) # timeout set for visual continuity on graph
        except SerialException:
            return False
        return True

    def get_data(self):
        """ Called by the consumer to get a packet of data """
        return self.queue.get_nowait()

    def quit_thread(self):
        """ Called by consumer when closing the capture activity."""
        self.quit = True

    def run(self):
        """ Class Thread override - the thread to run """
        self.quit = False
        msg = []
        while(1):
            try:
                abyte = self.source.read(1)
            except SerialException:
                if self.quit:
                    break
            msg.append(abyte)
            if abyte != '\n':
                continue

            # received end of line - what we need for a packet
            line = "".join(msg)
            line.strip(" \r\n")
            data = [float(x) for x in line.split(',')]
            data = data[:max_signal_count] # limit data to just what system is capable of.
            valid_bitmask = (1 << (len(data) + 1)) - 1 # mark all bits '1' for signals that are valid in the packet

            # compose a packet and buffer it up
            self.queue.put((self.timestamp(), valid_bitmask, data))

    def timestamp(self):
        return time() - self.start_time

