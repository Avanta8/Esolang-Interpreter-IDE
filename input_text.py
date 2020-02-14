import codecs
import re
from string import printable

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes


ASCII_PRINTABLE = set(printable)


class BaseDecoder:
    @classmethod
    def decode_next(cls, text):
        return '', 0


class BrainfuckDecoder(BaseDecoder):
    REGEX = re.compile(r'\\(?:n|r|t|\\|\d{1,3})|.', flags=re.DOTALL)

    @classmethod
    def decode_next(cls, text):
        match_obj = re.match(cls.REGEX, text)
        if match_obj is None:
            return None, 0

        # Matched string
        match = match_obj[0]

        # A match of length 1 means that the match was just a standard chararacter.
        # A match of more than length 1 means that the match was an escape sequence
        if len(match) > 1:
            if match[1].isdecimal():
                # Ascii code
                match = chr(int(match[1:]))
            else:
                # Escape character (\n, \r, \t)
                match = codecs.decode(match, 'unicode_escape')
        return match, match_obj.end()


class StandardInputText(QtWidgets.QPlainTextEdit):

    DECODERS = {
        FileTypes.NONE: BaseDecoder,
        FileTypes.BRAINFUCK: BrainfuckDecoder,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_char_format = QtGui.QTextCharFormat()
        # self.default_char_format.setBackground(QColor(Qt.green))

        self._reset()

    def restart(self):
        self._reset()

    def _reset(self):
        self.prev_input_indexes = [0, 0]

    def next_(self):
        text = self.toPlainText()
        last_input = self.prev_input_indexes[-1]

        char, length = self.decoder.decode_next(text[last_input:])
        if char is None:
            return None

        self.document().clearUndoRedoStacks()
        self.prev_input_indexes.append(last_input + length)

        return char

    def prev(self):
        self.prev_input_indexes.pop()

    def set_filetype(self, filetype):
        self.decoder = self.DECODERS[filetype]

    def canInsertFromMimeData(self, source):
        return source.hasText() and self._can_add_text()

    def insertFromMimeData(self, source):
        if not self.canInsertFromMimeData(source):
            return

        self.textCursor().insertText(source.text(), self.default_char_format)

    def _can_add_text(self):
        """Return whether it would be valid for text to be inserted at the current cursor position."""
        return self.textCursor().selectionStart() >= self.prev_input_indexes[-1]

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        textcursor = self.textCursor()

        if text in ASCII_PRINTABLE:
            if self._can_add_text():
                textcursor.insertText(text, self.default_char_format)
        elif key == QtCore.Qt.Key_Backspace:
            if textcursor.hasSelection() and self._can_add_text() or textcursor.position() - 1 >= self.prev_input_indexes[-1]:
                textcursor.deletePreviousChar()
        elif key == QtCore.Qt.Key_Delete:
            if self._can_add_text():
                textcursor.deleteChar()
        else:
            super().keyPressEvent(event)


class HighlighInputText(StandardInputText):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_char_format = QtGui.QTextCharFormat()
        self.highlight_char_format.setBackground(QtGui.QColor(QtCore.Qt.gray))

    def restart(self):
        self.remove_prev_highlight()
        self._reset()

    def next_(self):
        self.remove_prev_highlight()
        char = super().next_()
        self.highlight_current()
        return char

    def prev(self):
        self.remove_prev_highlight()
        super().prev()
        self.highlight_current()

    def highlight_current(self):
        start = self.prev_input_indexes[-2]
        end = self.prev_input_indexes[-1]

        self.format_range(start, end, self.highlight_char_format)

    def remove_prev_highlight(self):
        start = self.prev_input_indexes[-2]
        end = self.prev_input_indexes[-1]

        self.format_range(start, end, self.default_char_format)

    def format_range(self, start, end, format_):
        textcursor = self.textCursor()
        textcursor.setPosition(start)
        textcursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        textcursor.setCharFormat(format_)
