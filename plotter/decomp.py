# -*- coding: utf-8 -*-
"""
Decompress binary data into plottable points
"""
from _struct import unpack

from plotter import logset # @UnresolvedImport
debug, info, warn, err = logset('decomp')

class DecompBinary():
    """ Task intended to be attached to a thread. This receives binary formatted data 
        and interprets it into data points to be further processed and graphed."""

    def __init__(self, queue):
        self.queue = queue

    def read_queue_task(self): # A slot which takes no params
        """ Run the task of reading the data source queue (which could be a serial port) """
        info("read_queue_task()")

        self.stop = False

        # initialize a co-routine used to simplify logic of building messages
        ipt = self.build_pt()
        next(ipt)

        source = FakeDataSource()
        msg = []
        for abyte in source.get_sample():
            msg.append(abyte)
            if self.stop:
                break

            # try:
            #    by = self.queue.get(timeout = 0.1)
            # except Empty:
            #    # timed out, which allows self.stop to be checked
            #    # but otherwise just keep trying to get data.
            #    continue

            # pass 'by' to the packager, and pkg
            pkg = ipt.send(abyte)
            if pkg != None:
                # a package was decoded, so put it in the data stream
                self.queue.put(pkg)
                timestamp , data_type, value = pkg
                if len(msg) < 10:
                    info("{:32s}{:f}, {}, {:f}".format(
                        " ".join(["{:02X}".format(b) for b in bytes(msg)]),
                        timestamp,
                        data_type,
                        value))
                else:
                    for i in range(0, len(msg), 8):
                        th8 = msg[i:min(i + 8, len(msg))]
                        info("{}".format(" ".join(["{:02X}".format(b) for b in th8])))
                msg = []
        self.finished.emit()

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
            for _i in [1, 2, 3]:
                by = yield None
                timestamp = (timestamp * 256) + by
            by = yield None
            data_type = by
            try:
                if self.id_slots[data_type] == None:
                    continue # restart search for valid characters
            except IndexError:
                continue # restart search for valid characters

            # get the conversion characteristics for the data field
            conv, mant, fract = self.id_slots[data_type]
            bys = []
            for _i in range(int((mant + fract + 1) / 8)):
                by = yield None
                bys.append(by)

            value = unpack(conv, bytes(bys))[0]
            value /= 1 << fract
            by = yield (timestamp / 1000000., data_type, value) # finally return a value

def main():
    """    """
    converter = DecompBinary()
    converter.read_queue_task()

if __name__ == "__main__":
    main()
