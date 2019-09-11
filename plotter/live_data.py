import sys
import numpy as np
from queue import Empty
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from serial.tools.list_ports import comports

import config
from get_csv import CSV_Buffer

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
        # self.scope.setClipToView(True)

        # Scroll window

        self.scroll = self.graphScroll.addPlot(title = "Select focus")
        # self.scroll.setClipToView(True)
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
        # The capture timer processes self.update, which captures data.
        self.capture_timer = pg.QtCore.QTimer()
        self.capture_timer.timeout.connect(self.update)

        # Port selection combobox features

        self.ComportCombo.addItems([a[0] for a in comports()])
        self.ComportCombo.currentIndexChanged.connect(self.com_port_changed)
        self.selected_com_port = self.ComportCombo.currentText()
        # a timer periodically updates the available ports
        self.comport_timer = pg.QtCore.QTimer()
        self.comport_timer.timeout.connect(self.update_comports)
        self.comport_timer.start(2000) # update every 2 seconds

    def onButtonToggle(self, checked):
        if(checked):
            if self.start_capture():
                self.comport_timer.stop()
            else:
                self.capture_Button.setChecked(False) # return to unchecked
        else:
            self.capture_thread.stop()
            self.capture_timer.stop()
            self.comport_timer.start(2000) # update every 2 seconds

    def start_capture(self):
        self.data = np.empty([self.plot_count, 100])
        self.tstamps = np.empty([self.plot_count, 100])
        self.ptr = [0 for _i in range(self.plot_count)]
        self.max_data = 0

        # start data capture thread which composes packets and buffers them
        self.capture_thread = CSV_Buffer(self.selected_com_port)
        if self.capture_thread.open():
            self.capture_thread.start()
            # start the local capture_timer that updates the plot data
            self.capture_timer.start(20) # mSec
            return True
        else:
            return False

    def update(self):
        for _i in range(100): # capture up to 100 samples per timeout
            try:
                timestamp, valid_channels, x_data = self.capture_thread.get_data()
            except Empty:
                break # stop capturing in this time period

            for channel in range(self.plot_count):
                if valid_channels & (1 << channel):
                    debug("DATA: time {:3.4f} chan {:1} val {:4.4}".format(timestamp, channel, x_data[channel]))
                    # set the data point
                    self.data[channel, self.ptr[channel]] = x_data[channel]
                    self.tstamps[channel, self.ptr[channel]] = timestamp
                    self.ptr[channel] += 1

                    # re-shape data storage if it gets filled up
                    debug("compare @{} {} {}".format(channel, self.ptr[channel], self.data.shape[1]))
                    if self.ptr[channel] >= self.data.shape[1]:
                        tmp = self.data
                        self.data = np.empty(self.data.shape[0], self.data.shape[1] * 2)
                        self.data[:tmp.shape[0], :tmp.shape[1]] = tmp

                        debug("RESIZE @{} {} {}".format(channel, self.data.shape[1], self.tstamps.shape[1]))

        # apply the updated data to the curves
        for channel in range(self.plot_count):
            i = self.ptr[channel]
            self.plots[channel].setData(self.tstamps[channel, :i], self.data[channel, :i])
            self.scroll_plots[channel].setData(self.tstamps[channel, :i], self.data[channel, :i])

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
