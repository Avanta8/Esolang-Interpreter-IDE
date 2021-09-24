import collections
from PyQt5 import QtCore, QtGui, QtWidgets


class OutputText(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setFamily('Consolas')
        self.setFont(font)
        self.setReadOnly(True)
        self.setMaximumBlockCount(1000)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

    def add_text(self, text):
        self.moveCursor(QtGui.QTextCursor.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def set_text(self, text):
        self.setPlainText(text)
        self.moveCursor(QtGui.QTextCursor.End)
        self.ensureCursorVisible()


class RunnerOutputText(OutputText):

    interrupt = QtCore.pyqtSignal()
    completed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._timer = QtCore.QTimer()
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._add_from_buffer)

        self._buffer = collections.deque()

        self._stopped = False

        self.interrupt.connect(self._timer.stop)

    def keyPressEvent(self, event):

        key = event.key()
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if key == QtCore.Qt.Key_C and modifiers == QtCore.Qt.ControlModifier:
            self.interrupt.emit()

        return super().keyPressEvent(event)

    def clear(self):

        self._buffer.clear()

        return super().clear()

    def buffer_text(self, text):
        self._buffer.appendleft(text)

    def _add_from_buffer(self):
        if not self._buffer:
            if self._stopped:
                self.completed.emit()
                self._timer.stop()
            return
        length = min(100, len(self._buffer))
        text = ''.join(self._buffer.pop() for _ in range(length))
        self.add_text(text)

    def stop(self):
        self._stopped = True

    def continue_(self):
        self._stopped = False
        self._timer.start()
