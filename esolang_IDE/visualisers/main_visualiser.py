from PyQt5 import QtCore, QtWidgets


class MainVisualiser(QtWidgets.QWidget):

    def __init__(
        self,
        parent=None,
        visualiser_widget=None,
        commands_widget=None,
        io_widget=None,
        flags=QtCore.Qt.WindowFlags(),
    ):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets(visualiser_widget, commands_widget, io_widget)

    def init_widgets(self, visualiser_widget, commands_widget, io_widget):

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(visualiser_widget)
        self.splitter.addWidget(commands_widget)
        self.splitter.addWidget(io_widget)

        self.statusbar = QtWidgets.QStatusBar(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter, stretch=1)
        layout.addWidget(self.statusbar)
        self.setLayout(layout)

    def insert_visualiser_widget(self, widget):
        self.splitter.insertWidget(0, widget)

    def closed(self):
        """Method called when the visualiser containing `self` is closed."""
        self.commands_frame.display_paused()
        self.command_stop()

    def show_status_message(self, message):
        self.statusbar.showMessage(message)
