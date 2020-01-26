from PyQt5 import QtCore, QtGui, QtWidgets

from notebook import Notebook
from code_text import CodeText


class EditorPage(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

    def init_widgets(self):
        self.code_text = CodeText(self)
        self.visualiser = QtWidgets.QWidget(self)
        self.code_runner = QtWidgets.QWidget(self)

        self.code_runner_dock_widget = QtWidgets.QDockWidget('Code Runner')
        self.visualiser_dock_widget = QtWidgets.QDockWidget('Visualiser')

        self.setCentralWidget(self.code_text)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.code_runner_dock_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.visualiser_dock_widget)


class EditorNotebook(Notebook):

    def new_page(self):
        # self.add_tab(EditorPage(), 'Untitled')
        self.add_tab_to_current(EditorPage(), 'Untitled')
