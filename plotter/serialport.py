''' serialport.py Wrapper of PySerial library '''
 
 
from serial.tools.list_ports import comports

from plotter import logset                  # @UnresolvedImport
debug, info, warn, err = logset('serial')


def port_available(self, portname):
    ''' Check if port is currently available '''
    ports = comports()
    if ports == None:
        return False
    names, _descs, _hdwrIDs = zip(*ports)
    return portname in names

def list_ports():
    ''' List the connected comm ports'''
    portnames = [a[0] for a in comports()]
    for portinfo in comports():
        portname, description, hdwrID = portinfo
        info("{} {} {}".format(portname, description, hdwrID))
    return portnames

