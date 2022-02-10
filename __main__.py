from gui_main_dialog import Main_Dialog
from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
ui = Main_Dialog()
ui.show()
sys.exit(app.exec_())