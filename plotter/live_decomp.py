from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
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
        self.curve1 = self.p1.plot(pen=(255,255,255,200))
        self.curve2 = self.p2.plot()
    
        # create the thread that collects the data stream
        self.queue = Queue()
        self.thread = QThread()
        self.obj = DecompBinary(self.queue)               # create Worker object and Thread here
        
        #self.obj.finished.connect(self.thread.quit)       # Connect Worker Signals to the Thread slots
        self.stop_capture.connect(self.obj.stop_thread)
        self.thread.started.connect(self.obj.read_queue_task)     # Connect Thread started signal to Worker slot
        self.obj.moveToThread(self.thread)                # Move the Worker object to the Thread object
        
        self.thread.finished.connect(self.thread_finished) # Thread finished signal
        info("Starting thread.")
        self.thread.start() # Start the thread        
        
        self.capture_Button.clicked.connect(self.capture_clicked)
        self.capture_Button.setCheckable(True)
        self.capture_Button.toggle()
        
    def capture_clicked(self):
        if self.capture_Button.isChecked():
            self.thread.start() # Start the thread 
            info("Un-checked. Starting thread.")
        else:
            info("Checked. Emitting stop capture")
            self.stop_capture.emit()
            
    @pyqtSlot()
    def thread_finished(self):
        """ slot called when thread finishes"""
        info("Thread finished.")
        pass

class DataUpdate():
    def __init__(self,queue,  curves, terms):
        self.curves = curves
        self.queue = queue
        self.terms = terms
        self.data = np.empty(100)  # @UndefinedVariable
        self.ptr = 0
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        
        while(1):
            try:
                package = self.queue.get(False)
            except(Empty):
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
        
        for curve, term in zip(self.curves, self.terms):    
            curve.setData(self.data[:self.ptr])
            if term:
                curve.setPos(-self.ptr, 0)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    

    # timer based threads which produce the data updates
    update1 = DataUpdate(window.queue, [window.curve1, window.curve2], [True,False])
    update1.timer.start(40)
    
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()