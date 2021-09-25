from PyQt5 import QtCore, QtGui, QtWidgets

from esolang_IDE.code_text import CodeText
from esolang_IDE.code_runner import CodeRunner
from esolang_IDE.visualisers import MainVisualiser


class CloseSignalDockWidget(QtWidgets.QDockWidget):

    close_signal = QtCore.pyqtSignal()

    def closeEvent(self, event):
        self.close_signal.emit()
        return super().closeEvent(event)


class EditorPage(QtWidgets.QMainWindow):

    visualiser_closed = QtCore.pyqtSignal()
    code_runner_closed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

    def init_widgets(self):

        self._code_text = CodeText()
        self._code_runner = CodeRunner()
        self._visualiser = MainVisualiser()

        self._code_runner_dock_widget = CloseSignalDockWidget('Code Runner')
        self._code_runner_dock_widget.setWidget(self._code_runner)

        self._visualiser_dock_widget = CloseSignalDockWidget('Visualiser')
        self._visualiser_dock_widget.setWidget(self._visualiser)

        self._visualiser_dock_widget.close_signal.connect(self.visualiser_closed.emit)
        self._code_runner_dock_widget.close_signal.connect(self.code_runner_closed.emit)

        self.setCentralWidget(self._code_text)

        # Hack to change the default size of the dock widgets.
        # Initially makes them as small as possible.
        self.open_visualiser()
        self.open_code_runner()
        self.resizeDocks(
            [self._visualiser_dock_widget, self._code_runner_dock_widget],
            [1, 1],
            QtCore.Qt.Vertical,
        )
        self.removeDockWidget(self._visualiser_dock_widget)
        self.removeDockWidget(self._code_runner_dock_widget)

    def open_visualiser(self):
        """Dock the `visualiser_dock_widget` if it is not already visible"""
        if not self._visualiser.isVisible():
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self._visualiser_dock_widget)
            # self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self._visualiser_dock_widget)
            # self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self._visualiser_dock_widget, QtCore.Qt.Vertical)
            self._visualiser_dock_widget.show()

    def open_code_runner(self):
        """Dock the `code_runner_dock_widget` if it is not already visible"""
        if not self._code_runner.isVisible():
            self.addDockWidget(
                QtCore.Qt.BottomDockWidgetArea, self._code_runner_dock_widget
            )
            self._code_runner_dock_widget.show()

    def get_code_text(self):
        return self._code_text

    def get_code_runner(self):
        return self._code_runner

    def get_visualiser(self):
        return self._visualiser
