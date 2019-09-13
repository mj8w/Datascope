import sys
import numpy as np
from queue import Empty
from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from serial.tools.list_ports import comports

# TODO: graph windows should expand if window is maximized
# TODO: Add grid lines
# TODO: Add optional grid lines
# TODO: Add optional value display with crosshairs
# TODO: scroll window should always be 100% - not mouse zoomable
# TODO: Implement the mouse select window zoom on main graph window
# TODO: Create a method to display state and state change - i.e. hold data value between samples
#        we don't want transitions to display as a gradual change between samples
# TODO: display the number of samples/sec seen on the selected display, perhaps a popup / tooltip

import config
from get_csv import CSV_Buffer

debug, info, warn, err = config.logset('decomp')

class PlotData():

    def __init__(self, scope, scroll, pen, name):
        self.scope = scope.plot(pen = pen, name = name)
        self.scroll = scroll.plot(pen = pen, name = name)
        self.size = 10000
        self.data = np.empty(self.size)
        self.tstamp = np.empty(self.size)
        self.ptr = 0

    def reset(self):
        self.data = np.empty(self.size)
        self.tstamp = np.empty(self.size)
        self.ptr = 0

    def set_point(self, timestamp, data):
        self.tstamp[self.ptr] = timestamp
        self.data[self.ptr] = data
        self.ptr += 1
        if self.ptr >= self.size:
            self.increase_storage()

    def increase_storage(self):
        new_sz = self.size + 10000

        tmp = self.tstamp
        self.tstamp = np.empty(new_sz)
        self.tstamp[:self.size] = tmp

        tmp = self.data
        self.data = np.empty(new_sz)
        self.data[:self.size] = tmp

        self.size = new_sz

    def display(self):
        self.scope.setData(self.tstamp[:self.ptr], self.data[:self.ptr])
        self.scroll.setData(self.tstamp[:self.ptr], self.data[:self.ptr])

    def limits(self): # returns tuple of beginning and end timestamps
        return(self.tstamp[0], self.tstamp[self.ptr - 1])

class MainWindow(QtWidgets.QMainWindow):
    """ Create the main window from the Qt Designer generated file """

    def __init__(self):
        super().__init__()
        # self.setupUi(self) # Set up the user interface from Designer.
        uic.loadUi('data_scope.ui', self)

        # Graph window

        self.scope = self.graph.addPlot(title = "Captured data")
        self.scope.setDownsampling(mode = 'peak')

        # Scroll window

        self.scroll = self.graphScroll.addPlot(title = "Select focus")
        self.scroll.setDownsampling(mode = 'peak')
        self.scroll.showAxis('bottom', False)

        self.plot_count = config.max_signal_count

        self.plot_data = [
            PlotData(self.scope, self.scroll, (0, 0, 255), "Blue"),
            PlotData(self.scope, self.scroll, (255, 0, 0), "Red"),
            PlotData(self.scope, self.scroll, (0, 255, 0), "Green"),
            PlotData(self.scope, self.scroll, (255, 255, 0), "Yellow"),
            ]

        # "Linear region" - selection in scroll window that controls viewing of main window

        self.lr = pg.LinearRegionItem([0, 1])
        self.lr.setZValue(-10)
        self.scroll.addItem(self.lr)

        def updatePlot():
            self.scope.setXRange(*self.lr.getRegion(), padding = 0)
            debug("updatePlot()")

        def updateRegion():
            x1, x2 = self.scope.getViewBox().viewRange()[0]
            self.lr.setRegion([x1, x2])
            debug("updateRegion([{}, {}])".format(x1, x2))

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

        # Misc static information

        self.shown_channels = 0 # bitmask of channels that actually have data

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

        for i in range(self.plot_count):
            self.plot_data[i].reset()
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

            self.shown_channels |= valid_channels
            for channel in range(self.plot_count):
                if valid_channels & (1 << channel):
                    debug("DATA: time {:3.4f} chan {:1} val {:4.4}".format(timestamp, channel, x_data[channel]))
                    # set the data point
                    self.plot_data[channel].set_point(timestamp, x_data[channel])

        # apply the updated data to the curves
        min_ts = 999999999999.0
        max_ts = 0.0
        for channel in range(self.plot_count):
            self.plot_data[channel].display()
            if self.shown_channels & (1 << channel):
                limmin, limmax = self.plot_data[channel].limits()
                min_ts = min(min_ts, limmin)
                max_ts = max(max_ts, limmax)

        debug("update setRegion {}, {}".format(min_ts, max_ts))
        self.lr.setRegion([min_ts, max_ts])

    def com_port_changed(self, _i):
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
