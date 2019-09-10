import sys
import numpy as np
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from serial.tools.list_ports import comports

import config

debug, info, warn, err = config.logset('decomp')

class MainWindow(QtWidgets.QMainWindow):
    """ Create the main window from the Qt Designer generated file """

    def __init__(self):
        super().__init__()
        # self.setupUi(self) # Set up the user interface from Designer.
        uic.loadUi('data_scope.ui', self)

        # Graph window

        self.scope = self.graph.addPlot(title = "Captured data")
        self.scope.setDownsampling(mode = 'peak')
        self.scope.setClipToView(True)

        # Scroll window

        self.scroll = self.graphScroll.addPlot(title = "Select focus")
        self.scroll.setClipToView(True)
        self.scroll.setDownsampling(mode = 'peak')
        self.scroll.showAxis('bottom', False)

        self.plot_count = config.max_signal_count

        self.plots = [
            self.scope.plot(pen = (255, 0, 0), name = "Red"),
            self.scope.plot(pen = (0, 255, 0), name = "Green"),
            self.scope.plot(pen = (0, 0, 255), name = "Blue"),
            self.scope.plot(pen = (255, 255, 0), name = "Yellow"),
            ]

        self.scroll_plots = [
            self.scroll.plot(pen = (255, 0, 0), name = "Red"),
            self.scroll.plot(pen = (0, 255, 0), name = "Green"),
            self.scroll.plot(pen = (0, 0, 255), name = "Blue"),
            self.scroll.plot(pen = (255, 255, 0), name = "Yellow"),
            ]

        # "Linear region" - selection in scroll window that controls viewing of main window

        self.lr = pg.LinearRegionItem([0, 100])
        self.lr.setZValue(-10)
        self.scroll.addItem(self.lr)

        def updatePlot():
            self.scope.setXRange(*self.lr.getRegion(), padding = 0)
            print("updatePlot()")

        def updateRegion():
            self.lr.setRegion(self.scope.getViewBox().viewRange()[0])
            print("updateRegion()")

        self.lr.sigRegionChanged.connect(updatePlot)
        self.scope.sigXRangeChanged.connect(updateRegion)
        updatePlot()

        # Capture button features

        # the capture button
        self.capture_Button.setCheckable(True)
        self.capture_Button.toggled.connect(self.onButtonToggle)
        # The timer processes self.update, which captures data.
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        # Port selection combobox features

        self.ComportCombo.addItems([a[0] for a in comports()])
        self.ComportCombo.currentIndexChanged.connect(self.com_port_changed)
        self.selected_com_port = self.ComportCombo.currentText()
        # a timer periodically updates the available ports
        self.comport_timer = pg.QtCore.QTimer()
        self.comport_timer.timeout.connect(self.update_comports)
        self.comport_timer.start(2000) # update every 2 seconds


    def start_capture(self):
        self.data = np.empty([self.plot_count, 100])
        self.ptr = [0 for _i in range(self.plot_count)]
        self.max_data = 0
        self.timer.start(20) # start the timer based thread which produces the data updates

    def onButtonToggle(self, checked):
        if(checked):
            self.start_capture()
        else:
            self.timer.stop()

    def update(self):
        channel = np.random.random_integers(0, 3)
        self.data.itemset((channel, self.ptr[channel]), np.random.normal())
        self.ptr[channel] += 1

        # re-shape data if it gets too big.
        if self.ptr[channel] >= self.data.shape[1]:
            print (self.data.shape)
            self.data.resize((self.plot_count, self.data.shape[1] * 2))
            print (self.data.shape)

        # apply the updated data to the curves
        i = self.ptr[channel]
        self.plots[channel].setData(self.data[channel, :i])
        self.scroll_plots[channel].setData(self.data[channel, :i])

        print("update setRegion")
        self.max_data = max(self.max_data, i)
        self.lr.setRegion([0, self.max_data])

    def com_port_changed(self, i):
        self.selected_com_port = self.ComportCombo.currentText()

    def update_comports(self):
        """ Called by timer service to update the list of comports """
        available = set([a[0] for a in comports()])

        shown = []
        for count in range(self.ComportCombo.count()):
            shown.append(self.ComportCombo.itemText(count))

        for a in available:
            if a not in shown:
                self.ComportCombo.addItem(a)
                shown.append(a)

        for s in shown:
            if s not in available:
                # find item to remove
                for count in range(self.ComportCombo.count()):
                    if self.ComportCombo.itemText(count) == s:
                        self.ComportCombo.removeItem(count)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
