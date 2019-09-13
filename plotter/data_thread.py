# -*- coding: utf-8 -*-
"""
Get csv formatted data from serial port and buffer for plotting
"""

from queue import Queue
from threading import Thread
from time import time

from config import logset, max_signal_count

debug, info, warn, err = logset('data')

class DataThread(Thread):
    """ Thread to receive data and format in a standard packet
        to be further processed and graphed.
    """

    def __init__(self):
        super().__init__()

        # queue to store data collected from the serial port
        self.queue = Queue()

        # set the time to offset against the timestamp
        self.start_time = time()

        self.quit = False
        self.daemon = True

    def open(self):
        """ Override in derived class to open data source. 
            Called by consumer when starting the capture activity. """
        return False

    def get_data(self):
        """ Called by the consumer to get a packet of data """
        return self.queue.get_nowait()

    def stop(self):
        """ Called by consumer when closing the capture activity."""
        self.quit = True

    def run(self):
        """ Class Thread override - the thread to run. 
            This thread should silently throw invalid data away. 
            Use debug() to diagnose any issues that occur. """
        self.quit = False
        debug("start run()")

    def timestamp(self):
        """ Used in run() to create a PC based timestamp if the data source 
            does not provide one itself. """
        return time() - self.start_time
