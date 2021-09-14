from PyQt5 import QtCore, QtGui, QtWidgets

from visualisers import MainVisualiser
from code_text import CodeText
from code_runner import CodeRunner


class CloseSignalDockWidget(QtWidgets.QDockWidget):

    close_signal = QtCore.pyqtSignal()

    def closeEvent(self, event):
        self.close_signal.emit()
        return super().closeEvent(event)


class EditorPage(QtWidgets.QMainWindow):

    text_changed = QtCore.pyqtSignal(QtWidgets.QWidget)

    def __init__(self, filetype, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO:
        # Perhaps disable the visualiser and code runner fileinfo.filetype is None.

        self.init_widgets()

        self.set_filetype(filetype)

        if text:
            self.code_text.setText(text)

    def init_widgets(self):
        self.code_text = CodeText(self)
        self.visualiser = MainVisualiser(self)
        self.code_runner = CodeRunner(self)

        self.code_text.textChanged.connect(self._code_text_changed)

        self.code_runner_dock_widget = CloseSignalDockWidget('Code Runner')
        self.code_runner_dock_widget.setWidget(self.code_runner)

        self.visualiser_dock_widget = CloseSignalDockWidget('Visualiser')
        self.visualiser_dock_widget.setWidget(self.visualiser)

        self.visualiser_dock_widget.close_signal.connect(self.visualiser.closed)

        self.setCentralWidget(self.code_text)

        self._text_has_changed = False

    def set_filetype(self, filetype):
        self._filetype = filetype

        self.code_text.set_filetype(filetype)
        self.visualiser.set_filetype(filetype)
        self.code_runner.set_filetype(filetype)


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

    @QtCore.pyqtSlot()
    def _code_text_changed(self):
        self.text_changed.emit(self)
