from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer
from queue import Queue, Empty

import pyqtgraph as pg
import sys
import numpy as np
from data_scope_ui import Ui_MainWindow

from decomp_thread import DecompBinary
     
from plotter import logset  # @UnresolvedImport
debug, info, warn, err = logset('decomp')
     
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """ Create the main window from the Qt Designer generated file """
    stop_capture = pyqtSignal()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self) # Set up the user interface from Designer.
        #self.graph.nextRow()
        
        lr = pg.LinearRegionItem([400,700])
        lr.setZValue(-10)
        
        self.p1 = self.graph.addPlot(title="Zoom on selected region")
        
        def updatePlot():
            self.p1.setXRange(*lr.getRegion(), padding=0)
        def updateRegion():
            lr.setRegion(self.p1.getViewBox().viewRange()[0])
            
        lr.sigRegionChanged.connect(updatePlot)
        self.p1.sigXRangeChanged.connect(updateRegion)
        updatePlot()

        self.p2 = self.graphScroll.addPlot(title="Region Selection")
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
        self.main_graph = self.p1.plot(pen=(255,255,255,200))
        self.scroll_graph = self.p2.plot()
    
        self.capture_Button.clicked.connect(self.capture_clicked)
        self.capture_Button.setCheckable(True)
        self.capture_Button.toggle()
        
        self.decoder = DecompBinary()   # the data source 
        self.data = np.empty(100)  # @UndefinedVariable
        self.ptr = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_update)
        self.timer.start(40) # collect data by repeatedly calling update
        
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
                
            timestamp, data_type, value = package 
            
            debug("{:f}, {}, {:f}".format(timestamp, data_type, value))
            
            self.data[self.ptr] = value
            self.ptr += 1
            
            # re-shape data if it gets too big.
            if self.ptr >= self.data.shape[0]:
                tmp = self.data
                self.data = np.empty(self.data.shape[0] * 2)
                self.data[:tmp.shape[0]] = tmp
        
        self.main_graph.setData(self.data[:self.ptr])
        self.scroll_graph.setData(self.data[:self.ptr])
        self.main_graph.setPos(-self.ptr, 0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()