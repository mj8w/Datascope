from PyQt5 import QtWidgets, QtGui
from PyQt5.uic import loadUi

import sys

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        loadUi("window.ui", self)

        self.label.setFont(QtGui.QFont('SansSerif', 30)) # change font type and size
 

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())