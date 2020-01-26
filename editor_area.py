from PyQt5 import QtCore, QtGui, QtWidgets

from notebook import Notebook
from code_text import CodeText


class EditorPage(QtWidgets.QMainWindow):
    def __init__(self, *args, filepath, filetype, text, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

        self.set_file_info(filepath, filetype)

        if text:
            self.code_text.setText(text)

    def init_widgets(self):
        self.code_text = CodeText(self)
        self.visualiser = QtWidgets.QWidget(self)
        self.code_runner = QtWidgets.QWidget(self)

        self.code_runner_dock_widget = QtWidgets.QDockWidget('Code Runner')
        self.visualiser_dock_widget = QtWidgets.QDockWidget('Visualiser')

        self.setCentralWidget(self.code_text)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.code_runner_dock_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.visualiser_dock_widget)

    def set_file_info(self, filepath, filetype):
        self.filepath = filepath
        self.filetype = filetype

    def get_file_info(self):
        return self.filepath, self.filetype

    def get_text(self):
        return self.code_text.text()


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
