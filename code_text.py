from PyQt5 import QtWidgets, QtGui, QtCore, Qsci

from constants import FileTypes
import lexers


class CodeText(Qsci.QsciScintilla):

    LEXERS = {
        FileTypes.NONE: lexers.NoneLexer,
        FileTypes.BRAINFUCK: lexers.BrainfuckLexer,
        FileTypes.PYTHON: lexers.NoneLexer,
    }

    # According to docs, The first 8 are normally used by lexers
    _current_position_indicator_number = 20

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_settings()
        self.configure_styles()

        self.setLexer(None)

        self._last_command_position = (0, 0)

    def init_settings(self):
        # self.setEolMode(Qsci.QsciScintilla.SC_EOL_LF)
        self.setWrapMode(Qsci.QsciScintilla.WrapNone)
        # self.setEolVisibility(True)

        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)

        self.setCaretLineVisible(True)

        self.SendScintilla(self.SCI_SETMULTIPLESELECTION, True)
        self.SendScintilla(self.SCI_SETADDITIONALSELECTIONTYPING, True)

        self.setMarginType(0, self.NumberMargin)
        self.setMarginWidth(0, 40)
        self.setMarginWidth(1, 0)

    def configure_styles(self):
        self.setCaretLineBackgroundColor(QtGui.QColor(245, 245, 245))
        self.setIndentationGuidesBackgroundColor(QtGui.QColor(211, 211, 211))
        self.setIndentationGuidesForegroundColor(QtGui.QColor(211, 211, 211))

        self.indicatorDefine(self.FullBoxIndicator, self._current_position_indicator_number)
        self.setIndicatorDrawUnder(True, self._current_position_indicator_number)
        self.setIndicatorForegroundColor(QtGui.QColor('grey'))
        self.setIndicatorOutlineColor(QtGui.QColor('grey'))

    def set_filetype(self, filetype):
        self.setLexer(self.LEXERS[filetype](self))

    def highlight_position(self, position, chars):
        self.SendScintilla(self.SCI_SETINDICATORCURRENT, self._current_position_indicator_number)
        self.SendScintilla(self.SCI_INDICATORCLEARRANGE, *self._last_command_position)
        self.SendScintilla(self.SCI_INDICATORFILLRANGE, position, chars)
        self._last_command_position = (position, chars)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    code_text = CodeText()
    window.setCentralWidget(code_text)
    window.show()
    app.exec_()
