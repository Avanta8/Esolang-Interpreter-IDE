from PyQt5 import QtCore, QtGui, QtWidgets


class OutputText(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        font = QtGui.QFont()
        font.setPointSize(9)
        font.setFamily('Source Code Pro')
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

    def keyPressEvent(self, event):

        key = event.key()
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if key == QtCore.Qt.Key_C and modifiers == QtCore.Qt.ControlModifier:
            self.interrupt.emit()

        return super().keyPressEvent(event)
