# -*- coding: utf-8 -*-
"""
Decompress binary data into plottable points


In this example, we want to accept a packet of values in the format

    <Identifier uint8_t == 0xAA>,<int32_t data>[4]  # Big endian

The decoding is hard coded here. It seems easier to hand code than to 
make a configuration system that handles all the possible protocol options

"""
from _struct import unpack

from serial import Serial, SerialException

from data_thread import DataThread

from init import NoConfig, logset
try:
    from config import config
except ModuleNotFoundError:
    raise NoConfig

debug, info, warn, err = logset('data')

class DecodeBinary(DataThread):
    """ Receives binary formatted data and interprets it into data
        points to be further processed and graphed.
    """

    def __init__(self, comport):
        super().__init__()

        self.comport = comport
        self.source = None
        self.max_signal_count = config["max_signal_count"]

        # co-routines may take some effort to understand
        # but they simplified the code significantly in this case.

        # initialize a co-routine called self.pipe, which calls self.packager().
        self.pipe = self.packager()
        next(self.pipe)

    def open(self):
        """ Open the source of data and set the queue to read from """
        try:
            self.source = Serial(self.comport, baudrate = 115200, timeout = 0.05) # timeout set for visual continuity on graph
        except SerialException:
            return False
        return True

    def run(self):
        """ Class Thread override - the thread to run """
        self.quit = False
        debug("start run()")
        msg = []
        while(1):
            try:
                abyte = self.source.read(1)
            except SerialException:
                if self.quit:
                    break
                continue

            # msg is accumulated just for debugging
            msg.append(abyte)

            # pass 'abyte' to the packager, and pkg gets yielded through the pipe
            # byte by byte the pipeline is primed, and most of the time the
            # pkg is not complete, so we get None as a result.
            pkg = self.pipe.send(abyte)
            if pkg == None:
                continue

            # a package was decoded, so put it in the data stream
            self.queue.put(pkg)

            # record the activity to the logging system
            tstamp, data_type, value = pkg

            if len(msg) < 20: # anything longer assume invalid message
                info("{:32s}{:f}, {}, {:f}".format(
                    " ".join(["{:02X}".format(b) for b in bytes(msg)]),
                    tstamp,
                    data_type,
                    value))
            else:
                for i in range(0, len(msg), 8):
                    th8 = msg[i:min(i + 8, len(msg))]
                    info("{}".format(" ".join(["{:02X}".format(b) for b in th8])))
            msg = []

    def packager(self):
        """ 
            Attempt to create a datapoint using the byte stream input 
            This is a coroutine. 
            a = yield b means "yield b", then wait for send(a) call,
               and then a = value passed.
        """
        by = yield None # get next byte, and None because packet is not complete
        while(1):
            while by != 0xAA:
                by = yield None

            # have deliminator, so collect data
            tstamp = self.timestamp()

            # collect 4 - 4 byte values
            bys = bytearray()
            for _ibyte in range(4 * 4):
                b = yield None
                bys.insert(b)

            d1, d2, d3, d4 = unpack(">iiii", bys)
            by = yield (tstamp, 0, (d1, d2, d3, d4))

