import sys
import numpy as np
from queue import Empty
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QColor
import pyqtgraph as pg
from serial.tools.list_ports import comports

# TODO: Add optional grid lines
# TODO: scroll window should always be 100% - not mouse zoomable
# TODO: Implement the mouse select window zoom on main graph window
# TODO: Create a method to display state and state change - i.e. hold data value between samples
#        we don't want transitions to display as a gradual change between samples
# TODO: display the number of samples/sec seen on the selected display, perhaps a popup / tooltip

from get_csv import CSV_Buffer
from plot_data import PlotData


    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x: lo = mid + 1
        else: hi = mid
    return lo

class MainWindow(QtWidgets.QMainWindow):
    """ Create the main window from the Qt Designer generated file """

    def __init__(self):
        super().__init__()
        # self.setupUi(self) # Set up the user interface from Designer.
        uic.loadUi('data_scope.ui', self)

        # Graph window

        self.scope = self.graph.addPlot()
        self.scope.setDownsampling(mode = 'peak')

        # Scroll window

        self.scroll = self.graphScroll.addPlot()
        self.scroll.setDownsampling(mode = 'peak')
        self.scroll.showAxis('bottom', False)

        self.plot_count = config.max_signal_count

        self.plot_data = [
            PlotData(self.scope, self.scroll, (0, 0, 255), "Blue"),
            PlotData(self.scope, self.scroll, (255, 0, 0), "Red"),
            PlotData(self.scope, self.scroll, (0, 255, 0), "Green"),
            PlotData(self.scope, self.scroll, (255, 255, 0), "Yellow"),
            ]

        # cross hair & Stats label

        self.vLine = pg.InfiniteLine(angle = 90, movable = False)
        self.hLine = pg.InfiniteLine(angle = 0, movable = False)
        self.scope.addItem(self.vLine, ignoreBounds = True)
        self.scope.addItem(self.hLine, ignoreBounds = True)

        def mouseMoved(pos):
            if self.scope.sceneBoundingRect().contains(pos):
                mousePoint = self.scope.vb.mapSceneToView(pos)
                point = mousePoint.x()
                print("point = {}".format(point))
                index = self.plot_data[0].index(point)
                if index is not None:
                    txt = ["<span style='background-color black'>{:1.3f} Sec.".format(self.plot_data[0].tstamp[index])]

                    for channel in range(self.plot_count):
                        if self.shown_channels & (1 << channel):
                            txt.append(self.plot_data[channel].crosshair_val_text(index))
                    print("  ".join(txt))
                    self.stats_Label.setText("  ".join(txt))
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())

        self.scope.scene().sigMouseMoved.connect(mouseMoved)

        # "Linear region" - selection in scroll window that controls viewing of main window

        self.region = pg.LinearRegionItem([0, 1])
        self.region.setZValue(-10)
        self.scroll.addItem(self.region)

        def updatePlot():
            minX, maxX = self.region.getRegion()
            self.scope.setXRange(minX, maxX, padding = 0)
            debug("updatePlot()")

        def updateRegion():
            x1, x2 = self.scope.getViewBox().viewRange()[0]
            self.region.setRegion([x1, x2])
            debug("updateRegion([{}, {}])".format(x1, x2))

        self.region.sigRegionChanged.connect(updatePlot)
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
        self.region.setRegion([min_ts, max_ts])

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
