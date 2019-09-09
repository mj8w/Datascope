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

        self.lr = pg.LinearRegionItem([0, 100])
        self.lr.setZValue(-10)

        self.plots = self.graph.addPlot(title = "Captured data")
        self.plots.setDownsampling(mode = 'peak')
        self.plots.setClipToView(True)

        def updatePlot():
            self.plots.setXRange(*self.lr.getRegion(), padding = 0)
            print("updatePlot()")

        def updateRegion():
            self.lr.setRegion(self.plots.getViewBox().viewRange()[0])
            print("updateRegion()")

        self.lr.sigRegionChanged.connect(updatePlot)
        self.plots.sigXRangeChanged.connect(updateRegion)
        updatePlot()

        self.scroll = self.graphScroll.addPlot(title = "Select focus")
        self.scroll.showAxis('bottom', False)
        self.scroll.addItem(self.lr)

        self.scroll.setClipToView(True)
        self.scroll.setDownsampling(mode = 'peak')

        self.curve1 = self.plots.plot()
        self.curve2 = self.scroll.plot()

        self.terms = [True, False]
        self.data = np.empty(100)
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

        for curve in [self.curve1, self.curve2]:
            curve.setData(self.data[:self.ptr])

        print("update setRegion")
        self.lr.setRegion([0, self.ptr])

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    # timer based threads which produce the data updates
    window.timer.start(20)

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
