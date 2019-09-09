import numpy as np
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
import sys
# from data_scope_ui import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    """ Create the main window from the Qt Designer generated file """

    def __init__(self):
        super().__init__()
        # self.setupUi(self) # Set up the user interface from Designer.
        uic.loadUi('data_scope.ui', self)
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

        self.graph.nextRow()
        self.p2 = self.graph.addPlot(title="Region Selection")
        self.p2.showAxis('bottom', False)
        self.p2.addItem(lr)
        # Allow data to accumulate. Array doubles in length whenever it is full. 
        # Use automatic downsampling and clipping to reduce the drawing load
        self.p1.setDownsampling(mode='peak')
        self.p2.setDownsampling(mode='peak')
        self.p1.setClipToView(True)
        self.p2.setClipToView(True)
        self.p1.setRange(xRange=[-100, 0])
        self.p1.setLimits(xMax=0)
        self.curve1 = self.p1.plot(pen=(255,255,255,200))
        self.curve2 = self.p2.plot()
class DataUpdate():
    def __init__(self, curves,terms):
        self.curves = curves
        self.terms = terms
        self.data = np.empty(100)  # @UndefinedVariable



        self.ptr = 0

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

    def update(self):
        self.data[self.ptr] = np.random.normal()
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
    update1 = DataUpdate([window.curve1, window.curve2], [True,False])
    update1.timer.start(20)

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
