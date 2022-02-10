from PyQt5 import QtCore, QtGui, QtWidgets

class alert_dialog(QtWidgets.QMessageBox):
	def __init__(self, msg, _parent, icon=QtWidgets.QMessageBox.Information):
		super().__init__(parent=_parent)
		self.setText(msg)
		self.setIcon(icon)
		self.setWindowTitle("Info")
		self.setStandardButtons(QtWidgets.QMessageBox.Ok)
		self.exec()


if __name__ == "__main__":
	import sys

	app = QtWidgets.QApplication(sys.argv)
	ui = alert_dialog("test")
	ui.show()
	sys.exit(app.exec_())