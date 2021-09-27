from PyQt5 import QtCore, QtWidgets
from .io_widget import IOWidget
from .commands_widget import CommandsWidget
from .visualiser_widgets import NoVisualiserWidget


class MainVisualiser(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):

        self._io_widget = IOWidget()
        self._commands_widget = CommandsWidget()
        self._visualiser_widget = NoVisualiserWidget()

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(self._visualiser_widget)
        self.splitter.addWidget(self._commands_widget)
        self.splitter.addWidget(self._io_widget)

        self.statusbar = QtWidgets.QStatusBar(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter, stretch=1)
        layout.addWidget(self.statusbar)
        self.setLayout(layout)

    def set_visualiser_type(self, visualiser_type):
        self._visualiser_widget.deleteLater()
        self._visualiser_widget = visualiser_type()

        self.splitter.insertWidget(0, self._visualiser_widget)

    def show_status_message(self, message):
        self.statusbar.showMessage(message)

    def get_io_widget(self):
        return self._io_widget

    def get_commands_widget(self):
        return self._commands_widget

    def get_visualiser_widget(self):
        return self._visualiser_widget
