
import numpy as np
from bisect import bisect_left

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

debug, info, warn, err = logset('decomp')

class PlotData():

    def __init__(self, scope, scroll, signal):
        self.name = signal["name"]
        self.color = signal["color"] # See pyqtgraph.mkColor()
        self.width = signal["width"]
        self.precision = signal["precision"]
        self.scale = signal["scale"]

        self.scope = scope.plot(pen = self.color, name = self.name)
        self.scroll = scroll.plot(pen = self.color, name = self.name)
        self.size = 10000
        self.data = np.empty(self.size)
        self.tstamp = np.empty(self.size)
        self.ptr = 0

    def reset(self):
        self.data = np.empty(self.size)
        self.tstamp = np.empty(self.size)
        self.ptr = 0

    def set_point(self, timestamp, data):
        self.tstamp[self.ptr] = timestamp
        self.data[self.ptr] = data * self.scale
        self.ptr += 1
        if self.ptr >= self.size:
            self.increase_storage()

    def increase_storage(self):
        new_sz = self.size + 10000

        tmp = self.tstamp
        self.tstamp = np.empty(new_sz)
        self.tstamp[:self.size] = tmp

        tmp = self.data
        self.data = np.empty(new_sz)
        self.data[:self.size] = tmp

        self.size = new_sz

    def display(self):
        self.scope.setData(self.tstamp[:self.ptr], self.data[:self.ptr])
        self.scroll.setData(self.tstamp[:self.ptr], self.data[:self.ptr])

    def limits(self): # returns tuple of beginning and end timestamps
        return(self.tstamp[0], self.tstamp[self.ptr - 1])

    def index(self, timestamp):
        """ return index to timestamp if it is in data set, otherwise return None """
        the_list = list(self.tstamp)
        i = bisect_left(the_list, timestamp, hi = self.ptr)
        if i > 0.0 and i != len(self.tstamp):
            return i
        return None

    def crosshair_val_text(self, index):
        return "<span style='color: #{}'>{}= {:>{}.{}f}</span>".format(self.color, self.name, self.data[index], self.width, self.precision)
