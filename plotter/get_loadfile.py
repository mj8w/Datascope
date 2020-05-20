# -*- coding: utf-8 -*-
"""
Get csv formatted data from a file and buffer for plotting
"""
from data_thread import DataThread

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

debug, info, warn, err = logset('data')

class LoadFile_Buffer(DataThread):
    """ reads csv formatted data from a file and converts it into data
        points to be further processed and graphed.
    """

    def __init__(self, file_name):
        super().__init__()
        self.max_signal_count = config["max_signal_count"]
        self.file_name = file_name

    def open(self):
        try:
            self.source = open(self.file_name, 'r')
        except Exception:
            return False
        return True

    def run(self):
        """ Class Thread override - the thread to run """
        debug("start run()")
        for line in self.source:
            line = line.strip(" \r\n")
            try:
                entry = [x for x in line.split(',')]
                entry = entry[:self.max_signal_count + 2] # limit data to just what system is capable of.
                
                tstamp = entry[0]
                valid_bitmask = entry[1] # all bits '1' for signals that are valid in the packet
                data = entry[2:]
                
                # compose a packet and buffer it up
                self.queue.put((tstamp, valid_bitmask, data))
                
                debug("{:3.4f} {} {!r}".format(tstamp, valid_bitmask, data))
            except ValueError:
                debug("*** line='{}' Failed to parse... ***".format(line))
                pass
