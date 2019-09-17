import tcn_gui
import sys
from PyQt5 import QtCore,QtGui,QtWidgets

class query_window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.
        self.ui.pushButton.clicked.connect(self.query_formula)
        # 給button 的 點選動作繫結一個事件處理函式


    def query_formula(self):
        # 此處編寫具體的業務邏輯