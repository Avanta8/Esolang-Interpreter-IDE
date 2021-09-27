from typing import Type
from string import printable

from PyQt5 import QtCore, QtGui, QtWidgets

from esolang_IDE.input_decoders import BaseDecoder


_ASCII_PRINTABLE = set(printable)


class StandardInputText(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        self.default_char_format = QtGui.QTextCharFormat()

        self._reset()

    def restart(self):
        self._reset()

    def _reset(self):
        self._prev_input_indexes = [0, 0]

    def next_(self):
        text = self.toPlainText()
        last_input = self._prev_input_indexes[-1]

        char, length = self.decoder.decode_next(text[last_input:])
        if char is None:
            return None

        self.document().clearUndoRedoStacks()
        self._prev_input_indexes.append(last_input + length)

        return char

    def prev(self):
        self._prev_input_indexes.pop()

    def set_decoder(self, decoder: Type[BaseDecoder]):
        self.decoder = decoder

    def canInsertFromMimeData(self, source):
        return source.hasText() and self._can_add_text()

    def insertFromMimeData(self, source):
        if not self.canInsertFromMimeData(source):
            return

        self.textCursor().insertText(source.text(), self.default_char_format)

    def _can_add_text(self):
        """Return whether it would be valid for text to be inserted at the current cursor position."""
        return self.textCursor().selectionStart() >= self._prev_input_indexes[-1]

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        textcursor = self.textCursor()

        if text in _ASCII_PRINTABLE:
            if self._can_add_text():
                textcursor.insertText(text, self.default_char_format)
                self.ensureCursorVisible()
        elif key == QtCore.Qt.Key_Backspace:
            if (
                textcursor.hasSelection()
                and self._can_add_text()
                or textcursor.position() - 1 >= self._prev_input_indexes[-1]
            ):
                textcursor.deletePreviousChar()
        elif key == QtCore.Qt.Key_Delete:
            if self._can_add_text():
                textcursor.deleteChar()
        else:
            super().keyPressEvent(event)


class HighlightInputText(StandardInputText):

    # An update request is emitted by next or prev, in case the
    # input text is used in a different thread.
    _update_request = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_char_format = QtGui.QTextCharFormat()
        self.highlight_char_format.setBackground(QtGui.QColor(QtCore.Qt.gray))

        self._current_highlight = (0, 0)

        self._update_request.connect(self.highlight_current)

    def restart(self):
        self.remove_prev_highlight()
        self._reset()

    def next_(self, update=0):
        """
        Return the next input character(s).

        `update`:
            - 0: don't update visual
            - 1: update visual (using same thread)
            - 2: update visual from main thread using
                a signal (Call this if you are using the input
                text in a different thread)
        """
        char = super().next_()

        if update == 1:
            self.highlight_current()
        elif update == 2:
            self._update_request.emit()

        return char

    def prev(self, update=0):
        """
        `update`:
            - 0: don't update visual
            - 1: update visual (using same thread)
            - 2: update visual from main thread using
                a signal (Call this if you are using the input
                text in a different thread)
        """
        super().prev()

        if update == 1:
            self.highlight_current()
        elif update == 2:
            self._update_request.emit()

    def highlight_current(self):
        self.remove_prev_highlight()

        self._current_highlight = tuple(self._prev_input_indexes[-2:])
        self.format_range(*self._current_highlight, self.highlight_char_format)

    def remove_prev_highlight(self):
        self.format_range(*self._current_highlight, self.default_char_format)

    def format_range(self, start, end, format_):
        textcursor = self.textCursor()
        textcursor.setPosition(start)
        textcursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        textcursor.setCharFormat(format_)

    def request_highlight_update(self):
        self._update_request.emit()
