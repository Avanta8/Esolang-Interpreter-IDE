from PyQt5 import QtCore, QtGui, QtWidgets

from notebook import Notebook
from visualiser import MainVisualiser
from code_text import CodeText


class CloseSignalDockWidget(QtWidgets.QDockWidget):

    close_signal = QtCore.pyqtSignal()

    def closeEvent(self, event):
        self.close_signal.emit()
        return super().closeEvent(event)


class EditorPage(QtWidgets.QMainWindow):
    def __init__(self, *args, filepath, filetype, text, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

        self.set_file_info(filepath, filetype)

        if text:
            self.code_text.setText(text)

    def init_widgets(self):
        self.code_text = CodeText(self)
        self.visualiser = MainVisualiser(self)
        self.code_runner = QtWidgets.QWidget(self)

        self.code_runner_dock_widget = CloseSignalDockWidget('Code Runner')
        self.code_runner_dock_widget.setWidget(self.code_runner)

        self.visualiser_dock_widget = CloseSignalDockWidget('Visualiser')
        self.visualiser_dock_widget.setWidget(self.visualiser)

        self.visualiser_dock_widget.close_signal.connect(self.visualiser.closed)

        self.setCentralWidget(self.code_text)

    def set_file_info(self, filepath, filetype):
        self.filepath = filepath
        self.filetype = filetype

        self.code_text.set_filetype(filetype)
        self.visualiser.set_filetype(filetype)
        # self.code_runner.set_filetype(filetype)

    def get_file_info(self):
        return self.filepath, self.filetype

    def get_text(self):
        return self.code_text.text()

    def open_visualiser(self):
        """Dock the `visualiser_dock_widget` if it is not already visible"""
        if self.visualiser.isVisible():
            return
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.visualiser_dock_widget)
        self.visualiser_dock_widget.show()

    def open_code_runner(self):
        """Dock the `code_runner_dock_widget` if it is not already visible"""
        if self.code_runner.isVisible():
            return
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.code_runner_dock_widget)
        self.code_runner_dock_widget.show()


class EditorNotebook(Notebook):

    def new_page(self, filename, filepath, filetype, text):
        # self.add_tab(EditorPage(filepath=filepath, filetype=filetype, text=text), filename or 'Untitled')
        self.add_tab_to_current(EditorPage(filepath=filepath, filetype=filetype, text=text), filename or 'Untitled')

    def set_current_file_info(self, filename, filepath, filetype):
        tabwidget = self.current_tabwidget()
        if tabwidget is not None:
            index = tabwidget.currentIndex()
            tabwidget.setTabText(index, filename)
            tabwidget.widget(index).set_file_info(filepath, filetype)

    def get_current_file_info(self):
        page = self.current_page()
        if page is None:
            return None
        return page.get_file_info()

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
