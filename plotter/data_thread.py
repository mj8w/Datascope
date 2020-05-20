# -*- coding: utf-8 -*-
"""
Get csv formatted data from serial port and buffer for plotting
"""

from queue import Queue
from threading import Thread
from time import time

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

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

        # a place to save the running data set in order to save to a file for later use
        self.csv_list = []

        self.quit = False
        self.daemon = True

    def save_csv_file(self, filename):
        """ save the collected data as a csv file that can be loaded for display. """
        # may want to replace this later because it will take up a lot of memory
        # could replace with a loop
        csv_str = "\r\n".join([",".join(list(ta)) for ta in self.csv_list])
        with open(filename, 'w') as csv_file:
            csv_file.write(csv_str)

    def save_csv_entry(self, pkg):
        tstamp, data_type, value = pkg
        csv_entry = [str(tstamp), str(data_type)]
        csv_entry.extend([str(v) for v in value])
        self.csv_list.append(tuple(csv_entry)) 

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
