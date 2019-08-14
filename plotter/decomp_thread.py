# -*- coding: utf-8 -*-
"""
Decompress binary data into plottable points
"""
from time import sleep
from queue import Queue
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from _struct import unpack

#try:
#    from config import configuration as cfg  # @UnusedImport
#except:
    
from config_default import configuration as cfg  # @Reimport

from fake_data import FakeDataSource

from plotter import logset  # @UnresolvedImport

debug, info, warn, err = logset('decomp')

class DecompBinary():
    """ Receives binary formatted data and interprets it into data
        points to be further processed and graphed.
    """

    def __init__(self):
        self.delim = cfg["pkg_delimiter"]
        
        # get the data size for each signal type
        self.id_slots = [None for _ in range(cfg["MAX_SIGNAL"])]
        for k in cfg:
            if cfg[k].__class__.__name__ == "Signal":
                self.id_slots[cfg[k].id] = cfg[k].precision
        info("{!r}".format(self.id_slots) )
        
        # initialize a co-routine used to simplify logic of building messages
        self.ipt = self.build_pt()
        next(self.ipt)
        
        self.source = FakeDataSource()

    def read_queue(self): # A slot which takes no params
        """ Read the data source, interpret the data into graphable points """
        info("read_queue()") 
        msg = []
        for abyte in self.source.get_sample():
            if abyte == None:   # None means buffer is empty - we have caught up
                info("caught up") 
                yield None
               
            msg.append(abyte)
                
            #try:
            #    by = self.queue.get(timeout = 0.1)
            #except Empty:
            #    # timed out, which allows self.stop to be checked
            #    # but otherwise just keep trying to get data.
            #    continue
            
            # pass 'by' to the packager, and pkg      
            pkg = self.ipt.send(abyte)
            if pkg != None:
                # a package was decoded, so put it in the data stream
                yield pkg

                # record the activity to the logging system                
                timestamp , data_type, value = pkg
                if len(msg) < 10:
                    debug("{:32s}{:f}, {}, {:f}".format(
                        " ".join(["{:02X}".format(b) for b in bytes(msg)]), 
                        timestamp, 
                        data_type, 
                        value))
                else:
                    for i in range(0,len(msg),8):
                        th8 = msg[i:min(i+8,len(msg))]
                        info("{}".format(" ".join(["{:02X}".format(b) for b in th8])))
                msg = []
                 
    def build_pt(self):
        """ 
            Attempt to create a datapoint using the byte stream input 
            - this is a coroutine. a = yield b means "yield b", then wait for send(a) call,
               and assign a to value passed.
        """
        by = yield None
        while(1):
            while by != self.delim:
                by = yield None
                
            # have delim - next get timestamp
            timestamp = yield None
            for _i in [1,2,3]:
                by = yield None
                timestamp = (timestamp * 256) + by
            by = yield None
            data_type = by
            try:
                if self.id_slots[data_type] == None:
                    continue # restart search for valid characters
            except IndexError:
                continue    # restart search for valid characters
            
            # get the conversion characteristics for the data field
            conv, mant, fract = self.id_slots[data_type]
            bys = []
            for _ in range(int((mant+fract+1)/8)):
                by = yield None
                bys.append(by)
            
            value = unpack(conv, bytes(bys))[0]
            value /= 1 << fract
            by = yield (timestamp / 1000000., data_type, value) #finally return a value

