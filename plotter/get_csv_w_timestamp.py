# -*- coding: utf-8 -*-
"""
Get csv formatted data from serial port and buffer for plotting
"""
from get_csv import CSV_Buffer

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

debug, info, warn, err = logset('data')

class CSV_TS_Buffer(CSV_Buffer):
    """ Receives csv formatted data and interprets it into data
        points to be further processed and graphed.
    """

    def __init__(self, comport):
        super().__init__(comport)

    def decode_line(self, data):
        """ Just need to override the way that a CSV line gets decoded so that we grab the timestamp from the CSV directly."""        
        tstamp = data[0] / 1000.0 # for timestamp in mS
        data = data[1:self.max_signal_count+1] # limit data to just what system is capable of.

        valid_bitmask = (1 << len(data)) - 1 # mark all bits '1' for signals that are valid in the packet

        # compose a packet and buffer it up
        self.queue.put((tstamp, valid_bitmask, data))
        self.save_csv_entry((tstamp, valid_bitmask, data))        # save entry in case we save the plot data to file later

        debug("{:3.4f} {} {!r}".format(self.tstamp, valid_bitmask, data))
