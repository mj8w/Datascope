''' serialport.py Wrapper of PySerial library '''

from serial import Serial
from serial.tools.list_ports import comports

from Seagull import logset
debug, info, warn, err = logset('serial')

class SerialPort():
    ''' Configure the serial port. '''

    def __init__(self, comport_name):
        ''' Uses pyserial library '''
        self.comport_name = comport_name
        if not self.port_available(self.comport_name):
            err(" Port {} is not available. List:".format(self.comport_name))
            self.list_ports()
            exit(1)
        
        self.serial = Serial(port=self.comport_name, baudrate=115200, timeout=0.05) # 50ms timeout.

    def port_available(self, portname):
        ''' Check if port is currently available '''
        ports = comports()
        if ports == None:
            return False
        names, _descs, _hdwrIDs = zip(*ports)
        return portname in names

    def list_ports(self):
        ''' List the connected comm ports'''
        for portinfo in comports():
            portname, description, hdwrID = portinfo
            info("{} {} {}".format(portname, description, hdwrID))

