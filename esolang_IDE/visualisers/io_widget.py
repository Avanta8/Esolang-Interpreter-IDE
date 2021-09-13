from PyQt5 import QtCore, QtWidgets

from input_text import HighlighInputText
from output_text import OutputText


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

        self.input_text = HighlighInputText(self)
        self.output_text = OutputText(self)
        self.error_text = QtWidgets.QLineEdit(self)

        self.error_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input:'))
        layout.addWidget(self.input_text)
        layout.addWidget(QtWidgets.QLabel('Output:'))
        layout.addWidget(self.output_text)
        layout.addWidget(self.error_text)
        self.setLayout(layout)

    def set_error_text(self, message):
        self._error_text_timer.stop()
        self.error_text.setText(message)
        self.error_text.show()
        self.error_text_active = True

    def timed_error_text(self, message, time=1000):
        self.set_error_text(message)
        self._error_text_timer.start(time)

    def clear_error_text(self):
        if not self.error_text_active:
            return
        self._error_text_timer.stop()
        self.error_text.clear()
        self.error_text.hide()
        self.error_text_active = False
