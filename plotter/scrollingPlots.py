# -*- coding: utf-8 -*-
"""
method of drawing scrolling plot.
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from numpy import random, empty

win = pg.GraphicsWindow()
win.setWindowTitle('pyqtgraph scrolling plot')

# Allow data to accumulate. Array doubles in length whenever it is full. 
win.nextRow()
p3 = win.addPlot()
p4 = win.addPlot()

# Use automatic downsampling and clipping to reduce the drawing load
p3.setDownsampling(mode='peak')
p4.setDownsampling(mode='peak')
p3.setClipToView(True)
p4.setClipToView(True)
p3.setRange(xRange=[-100, 0])
p3.setLimits(xMax=0)
curve3 = p3.plot()
curve4 = p4.plot()

class DataUpdate():
    def __init__(self, curve,term):
        self.curve = curve
        self.term = term
        self.data = np.empty(100)  # @UndefinedVariable
        self.ptr = 0
        
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        

    def update(self):
        self.data[self.ptr] = random.normal()
        self.ptr += 1
        
        # re-shape data if it gets too big.
        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            self.data = empty(self.data.shape[0] * 2)
            self.data[:tmp.shape[0]] = tmp
            
        self.curve.setData(self.data[:self.ptr])
        if self.term:
            self.curve.setPos(-self.ptr, 0)
    
update4 = DataUpdate(curve4, False)
update4.timer.start(25)

update3 = DataUpdate(curve3, True)
update3.timer.start(25)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
