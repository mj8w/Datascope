import sys
from PyQt5.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Combo boxes")
        self.setGeometry(50,50,500,500)
        self.UI()
    
    def UI(self):
        self.cb = QComboBox(self)
        self.cb.move(150,100)
        list1 = ["a", "b", "help"]
        self.cb.addItems(list1)
        
        
        self.button=QPushButton("save", self)
        self.button.move(150,130)
        self.show()

        
def main():
    app = QApplication(sys.argv)
    _ = Window()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
