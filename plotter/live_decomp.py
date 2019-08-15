

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer
from queue import Queue, Empty
from serialport import Serial, list_ports
import pyqtgraph as pg
import sys
import numpy as np
from data_scope_ui import Ui_MainWindow

from decomp_thread import DecompBinary

#try:
#    from config import configuration as cfg  # @UnusedImport
#except:
    
from config_default import configuration as cfg  # @Reimport
     
from plotter import logset  # @UnresolvedImport
debug, info, warn, err = logset('decomp')
     
class PlotData():
    """ Control the contents of an individual plot"""
    def __init__(self, signal, plot):
        self.signal = signal
        self.plot = plot
        self.data = np.empty(100)
        self.timestamp = np.empty(100)
        self.ptr = 0
             
    def addData(self, timestamp, value):
        """ Add data to this stream... """
        # re-shape data if it gets too big.
        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            self.data = np.empty(self.data.shape[0] * 2)
            self.data[:tmp.shape[0]] = tmp
            tmp = self.timestamp
            self.timestamp = np.empty(self.timestamp.shape[0] * 2)
            self.timestamp[:tmp.shape[0]] = tmp
        
        self.data[self.ptr] = value
        self.timestamp[self.ptr] = timestamp
        self.ptr += 1
        
        # TODO: Add timestamp data
        self.plot.setData(self.data[:self.ptr])
        self.plot.setPos(-self.ptr, 0)
     
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """ Create the main window from the Qt Designer generated file """
    stop_capture = pyqtSignal()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self) # Set up the user interface from Designer.
        #self.graph.nextRow()
        
        lr = pg.LinearRegionItem([400,700])
        lr.setZValue(-10)
        
        self.p1 = self.graph.getPlotItem()
        
        def updatePlot():
            self.p1.setXRange(*lr.getRegion(), padding=0)
        def updateRegion():
            lr.setRegion(self.p1.getViewBox().viewRange()[0])
            
        lr.sigRegionChanged.connect(updatePlot)
        self.p1.sigXRangeChanged.connect(updateRegion)
        updatePlot()

        self.p2 = self.graphScroll.getPlotItem()
        self.p2.showAxis('bottom', False)
        self.p2.addItem(lr)
              
        # Allow data to accumulate. Array doubles in length whenever it is full. 
        # Use automatic downsampling and clipping to reduce the drawing load
        self.p1.setDownsampling(mode='peak')
        self.p2.setDownsampling(mode='peak')
        self.p1.setClipToView(True)
        self.p2.setClipToView(True)
        self.p1.setRange(xRange=[-1000, 0])
        self.p1.setLimits(xMax=0)
        
        self.main_graphs = []
        
        # get the metadata about each signal
        # add a plot curve for each signal.
        self.plot_datas = [None for _ in range(cfg["MAX_SIGNAL"])]
        for k in cfg:
            if cfg[k].__class__.__name__ == "Signal":
                self.plot_datas[cfg[k].id] = PlotData(cfg[k], self.p1.plot())
        
        # create smaller graph to show the overall capture
        self.scroll_graph = self.p2.plot()
    
        # button to control the capture of data
        self.capture_Button.setCheckable(True)
        self.capture_Button.toggle()
        self.capture_Button.clicked.connect(self.capture_clicked)
        
        # Combo that contains comports to connect to
        
        ports = list_ports()
        
        self.ComportCombo.addItems(ports)
        self.ComportCombo.currentIndexChanged.connect(self.commPort_selectionchange)
        
        self.decoder = DecompBinary()   # the data source 
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_update)

    def commPort_selectionchange(self,i):
        info("Comport Items are :{!r}".format(
            [ self.ComportCombo.itemText(count) for count in range(self.ComportCombo.count())]
            ))
        info("Current port = {}".format(self.ComportCombo.currentText()))
        
    def capture_clicked(self):
        if self.capture_Button.isChecked(): # if is Checked, currently capturing data
            self.timer.stop()
        else:
            self.timer.start(40) # 25 Hz
            
    @pyqtSlot()
    def thread_finished(self):
        """ slot called when thread finishes"""
        info("Thread finished.")
        pass

    def on_update(self):
        """ When update timer expires, read all of the contents of the incoming data stream, and 
            add the data to the graph.
        """
        for package in self.decoder.read_queue():
            if package == None:
                break
            break # TODO remove
        """        
            timestamp, data_type, value = package 
            debug("{:f}, {}, {:f}".format(timestamp, data_type, value))
            self.plot_datas[data_type].addData(timestamp, value)
        """

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()