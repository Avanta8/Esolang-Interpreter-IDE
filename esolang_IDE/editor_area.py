from PyQt5 import QtCore, QtGui, QtWidgets

from notebook import Notebook
from visualisers import MainVisualiser
from code_text import CodeText
from code_runner import CodeRunner


class CloseSignalDockWidget(QtWidgets.QDockWidget):

    close_signal = QtCore.pyqtSignal()

    def closeEvent(self, event):
        self.close_signal.emit()
        return super().closeEvent(event)


class EditorPage(QtWidgets.QMainWindow):

    text_changed = QtCore.pyqtSignal()

    def __init__(self, fileinfo, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

        self.set_fileinfo(fileinfo)

        if text:
            self.code_text.setText(text)

    def init_widgets(self):
        self.code_text = CodeText(self)
        self.visualiser = MainVisualiser(self)
        self.code_runner = CodeRunner(self)

        self.code_text.textChanged.connect(self.text_changed.emit)

        self.code_runner_dock_widget = CloseSignalDockWidget('Code Runner')
        self.code_runner_dock_widget.setWidget(self.code_runner)

        self.visualiser_dock_widget = CloseSignalDockWidget('Visualiser')
        self.visualiser_dock_widget.setWidget(self.visualiser)

        self.visualiser_dock_widget.close_signal.connect(self.visualiser.closed)

        self.setCentralWidget(self.code_text)

    def set_fileinfo(self, fileinfo):
        self.fileinfo = fileinfo

        self.code_text.set_filetype(fileinfo.filetype)
        self.visualiser.set_filetype(fileinfo.filetype)
        self.code_runner.set_filetype(fileinfo.filetype)

    def get_fileinfo(self):
        return self.fileinfo

    def get_text(self):
        return self.code_text.text()

    def open_visualiser(self):
        """Dock the `visualiser_dock_widget` if it is not already visible"""
        if not self.visualiser.isVisible():
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.visualiser_dock_widget)
            self.visualiser_dock_widget.show()

    def open_code_runner(self):
        """Dock the `code_runner_dock_widget` if it is not already visible"""
        if not self.code_runner.isVisible():
            self.addDockWidget(
                QtCore.Qt.BottomDockWidgetArea, self.code_runner_dock_widget
            )
            self.code_runner_dock_widget.show()
        self.code_runner.run_code()


class EditorNotebook(Notebook):
    def new_page(self, fileinfo, text):
        page = EditorPage(fileinfo, text)
        self.add_tab_to_current(page, fileinfo.filename or 'Untitled')

    def set_current_fileinfo(self, fileinfo):
        tabwidget = self.current_tabwidget()
        if tabwidget is not None:
            index = tabwidget.currentIndex()
            tabwidget.setTabText(index, fileinfo.filename)
            tabwidget.widget(index).set_fileinfo(fileinfo)

    def get_current_fileinfo(self):
        page = self.current_page()
        if page is None:
            return None
        return page.get_fileinfo()

    def get_current_text(self):
        page = self.current_page()
        if page is None:
            return None
        return page.get_text()

    def open_visualiser(self):
        page = self.current_page()
        if page is None:
            return
        page.open_visualiser()

    def open_code_runner(self):
        page = self.current_page()
        if page is None:
            return
        page.open_code_runner()
