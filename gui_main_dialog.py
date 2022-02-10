# Form implementation generated from reading ui file 'GUI/main_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.1 and edited by IBP
#
# To implement:
#   * Cache last selected folder
#   * Batch mode for multiple input folders and a single output
#   * Uncaugth exception handling

from PyQt5 import QtCore, QtWidgets
from group_summarizer import summarize_signal_probability_along_line
from alert_dialog import alert_dialog
import pathlib
from subprocess import Popen as subprocess_Popen
from constants import FILES_BROWSER_COMMAND, __APP_NAME__
import json

qtranslate = QtCore.QCoreApplication.translate

class Main_Dialog(QtWidgets.QDialog):
    '''
    WIP! Deal with reject event!
    '''
    def __init__(self):
        super().__init__()
        self.__cache_path = pathlib.Path.home().joinpath(__APP_NAME__)
        self.setObjectName("main_dialog")
        self.resize(356, 229)
        self.btn_ok = QtWidgets.QDialogButtonBox(self)
        self.btn_ok.setGeometry(QtCore.QRect(170, 200, 161, 21))
        self.btn_ok.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel)
        self.btn_ok.setObjectName("btn_ok")
        self.txt_csv_root = QtWidgets.QLineEdit(self)
        self.txt_csv_root.setGeometry(QtCore.QRect(20, 40, 271, 20))
        self.txt_csv_root.setObjectName("csv_root")
        self.txt_summary_dir = QtWidgets.QLineEdit(self)
        self.txt_summary_dir.setGeometry(QtCore.QRect(20, 90, 271, 20))
        self.txt_summary_dir.setObjectName("summary_dir")
        self.lbl_summary = QtWidgets.QLabel(self)
        self.lbl_summary.setGeometry(QtCore.QRect(20, 70, 121, 16))
        self.lbl_summary.setObjectName("lbl_summary")
        self.lbl_csv = QtWidgets.QLabel(self)
        self.lbl_csv.setGeometry(QtCore.QRect(20, 20, 121, 16))
        self.lbl_csv.setObjectName("lbl_csv")
        self.lbl_th = QtWidgets.QLabel(self)
        self.lbl_th.setGeometry(QtCore.QRect(200, 120, 70, 13))
        self.lbl_th.setObjectName("lbl_th")
        self.lbl_bin = QtWidgets.QLabel(self)
        self.lbl_bin.setGeometry(QtCore.QRect(20, 120, 70, 13))
        self.lbl_bin.setObjectName("lbl_bin")
        self.bin_size = QtWidgets.QSpinBox(self)
        self.bin_size.setGeometry(QtCore.QRect(20, 150, 50, 22))
        self.bin_size.setMinimum(1)
        self.bin_size.setMaximum(100)
        self.bin_size.setSingleStep(5)
        self.bin_size.setProperty("value", 1)
        self.bin_size.setObjectName("sldr_bin_size")
        self.th = QtWidgets.QSpinBox(self)
        self.th.setGeometry(QtCore.QRect(200, 150, 50, 22))
        self.th.setMinimum(1)
        self.th.setMaximum(100)
        self.th.setSingleStep(5)
        self.th.setProperty("value", 70)
        self.th.setObjectName("sldr_th")
        self.btn_csv_root = QtWidgets.QToolButton(self)
        self.btn_csv_root.setGeometry(QtCore.QRect(300, 40, 31, 20))
        self.btn_csv_root.setObjectName("btn_csv_root")
        self.btn_summary_dir = QtWidgets.QToolButton(self)
        self.btn_summary_dir.setGeometry(QtCore.QRect(300, 90, 31, 20))
        self.btn_summary_dir.setObjectName("btn_summary_dir")
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setGeometry(QtCore.QRect(20, 200, 141, 20))
        self.check_show_results = QtWidgets.QCheckBox(self)
        self.check_show_results.setGeometry(QtCore.QRect(210, 70, 121, 17))
        self.check_show_results.setObjectName("check_show_results")
        self.retranslateUi()
        self.connect_signals()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.append_to_cache(("txt_summary_dir", "text"),
            ("txt_csv_root", "text"),
            ("th", "value"),
            ("bin_size", "value"))
        self.init_cache()

    def closeEvent(self, event):
        self.cache_LIFO()
        super(QtWidgets.QDialog, self).closeEvent(event)


    def init_cache(self):
        try:
            self.__cache_path.mkdir(parents=True)
        except FileExistsError:
            pass
        self.__cache_file = self.__cache_path.joinpath("cache.json")

        if self.__cache_file.exists():
            with self.__cache_file.open(encoding="utf8") as cache_file:
                self.__LIFO = json.load(cache_file, parse_float=True)
        else:
            self.update_LIFO()
        self.display_LIFO()


    def display_LIFO(self):
        for k, v in self.__LIFO.items():
            getattr(getattr(self, k), f"set{v[0].capitalize()}")(v[1])


    def update_LIFO(self):
        self.__LIFO = {field[0]: [field[1], getattr(getattr(self, field[0]), field[1])()]
            for field
            in self.remember}


    def cache_LIFO(self):
        self.update_LIFO()
        with self.__cache_file.open(encoding="utf8", mode="w") as cache_file:
            json.dump(self.__LIFO, cache_file, indent=2)


    def append_to_cache(self, *args):
        self.remember = []
        for field in args:
            self.remember.append(field)


    def connect_signals(self)->None:
        self.btn_ok.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.execute)
        self.btn_ok.rejected.connect(self.reject)
        self.btn_csv_root.clicked.connect(self.choose_directory)
        self.btn_summary_dir.clicked.connect(self.choose_directory)


    def retranslateUi(self)->None:
        self.setWindowTitle(qtranslate(self.objectName(), "IBPlib - Bin Coverage Score"))
        self.lbl_summary.setText(qtranslate(self.objectName(), "Summary directory"))
        self.lbl_csv.setText(qtranslate(self.objectName(), "Raw data directory"))
        self.lbl_th.setText(qtranslate(self.objectName(), "Threshold (%)"))
        self.lbl_bin.setText(qtranslate(self.objectName(), "Bin size (%)"))
        self.btn_csv_root.setText(qtranslate(self.objectName(), "..."))
        self.btn_summary_dir.setText(qtranslate(self.objectName(), "..."))
        self.check_show_results.setText(qtranslate("main_dialog", "Show results"))


    def choose_directory(self)->None:
        '''
        Opens QFileDialog to select a directory and stores this value
        on txt field of the same base name as the signal sender.
        '''
        fdialog = QtWidgets.QFileDialog(self)
        fdialog.setFileMode(QtWidgets.QFileDialog.Directory)
        fdialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        boundInput = f"txt_{self.getSenderRootName()}"
        directory = fdialog.getExistingDirectory(self, qtranslate(self.objectName(), "Select folder..."))
        getattr(self, boundInput).setText(directory)


    def getSenderRootName(self)->str:
        '''
        Extracts the root name of a given Qobject
        Eg. If self.sender().objectName() is 'btn_username'
        return value would be 'username'.
        '''
        name = self.sender().objectName()
        root = name.split("_", maxsplit = 1)[1]
        return root


    def collect_form_data(self)->tuple:
        '''
        Gather the input form data.
        Returns a tuple containing
        [0] csv directory
        [1] output directory
        [2] bin sie
        [3] threshold value (between 0 and 1)
        '''
        form_data = [
            self.txt_csv_root.text(),
            self.txt_summary_dir.text(),
            self.bin_size.value()/100,
            self.th.value()/100]

        for arg, field in zip(form_data, (self.txt_csv_root,
            self.txt_summary_dir,
            self.bin_size,
            self.th)):
            if not arg:
                self.alert(f"Please fill in the {field.objectName()} field.")
                return

        form_data[0] = pathlib.Path(form_data[0])
        form_data[1] = pathlib.Path(form_data[1])
        return form_data


    def execute(self)->None:
        '''
        Calls the group_summarizer script with the form data as params
        '''
        _args = self.collect_form_data()
        if not _args:
            return

        self.progress_bar.setRange(0,0)
        try:
            summarize_signal_probability_along_line(*_args, std_out=self.alert)
        except Exception as e:
            self.progress_bar.setRange(0,100)
            self.alert(f"ERROR\n{str(e)}", icon=QtWidgets.QMessageBox.Critical)
        else:
            self.progress_bar.setRange(0,100)
            self.alert("Done summarizing data.", icon=QtWidgets.QMessageBox.Information)
            try:
                if self.check_show_results.isChecked():
                    subprocess_Popen([*FILES_BROWSER_COMMAND, str(_args[1])])
            except Exception as e:
                self.alert(f"Something went wrong while trying to show the results.\n{e.args[0]}")


    def alert(self, msg, icon=QtWidgets.QMessageBox.Information)->None:
        '''
        Wrapper to create a QMessageBox with the input message
        '''
        alert_dialog(msg, self, icon=icon)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Main_Dialog()
    ui.show()
    sys.exit(app.exec_())