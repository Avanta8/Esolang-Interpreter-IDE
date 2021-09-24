from PyQt5 import QtCore, QtWidgets

from esolang_IDE.input_text import HighlightInputText
from esolang_IDE.output_text import OutputText


class IOWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

        self.error_text_active = True
        self.clear_error_text()

    def init_widgets(self):
        self._error_text_timer = QtCore.QTimer(self)
        self._error_text_timer.setSingleShot(True)
        self._error_text_timer.timeout.connect(self.clear_error_text)

        self._input_text = HighlightInputText(self)
        self._output_text = OutputText(self)
        self._error_text = QtWidgets.QLineEdit(self)

        self._error_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input:'))
        layout.addWidget(self._input_text)
        layout.addWidget(QtWidgets.QLabel('Output:'))
        layout.addWidget(self._output_text)
        layout.addWidget(self._error_text)
        self.setLayout(layout)

    def set_error_text(self, message):
        self._error_text_timer.stop()
        self._error_text.setText(message)
        self._error_text.show()
        self.error_text_active = True

    def timed_error_text(self, message, time=1000):
        self.set_error_text(message)
        self._error_text_timer.start(time)

    def clear_error_text(self):
        if not self.error_text_active:
            return
        self._error_text_timer.stop()
        self._error_text.clear()
        self._error_text.hide()
        self.error_text_active = False

    def get_input_text(self):
        return self._input_text
    
    def get_output_text(self):
        return self._output_text
