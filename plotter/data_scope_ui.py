# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data_scope.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(838, 581)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, 9, 821, 561))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.graph = GraphicsWindow(parent=self.horizontalLayoutWidget)
        self.graph.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.graph.setObjectName("graph")
        self.verticalLayout.addWidget(self.graph)
        self.graphScroll = GraphicsWindow(parent=self.horizontalLayoutWidget)
        self.graphScroll.setMaximumSize(QtCore.QSize(16777215, 150))
        self.graphScroll.setFrameShadow(QtWidgets.QFrame.Raised)
        self.graphScroll.setObjectName("graphScroll")
        self.verticalLayout.addWidget(self.graphScroll)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.capture_Button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.capture_Button.setMaximumSize(QtCore.QSize(80, 16777215))
        self.capture_Button.setObjectName("capture_Button")
        self.verticalLayout_2.addWidget(self.capture_Button)
        self.save_Button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.save_Button.setMaximumSize(QtCore.QSize(80, 16777215))
        self.save_Button.setObjectName("save_Button")
        self.verticalLayout_2.addWidget(self.save_Button)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 838, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Data Scope"))
        self.capture_Button.setText(_translate("MainWindow", "Capture"))
        self.save_Button.setText(_translate("MainWindow", "Save"))
        self.pushButton.setText(_translate("MainWindow", "Load"))

from pyqtgraph import GraphicsWindow
