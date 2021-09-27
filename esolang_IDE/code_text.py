from PyQt5 import QtWidgets, QtGui, QtCore, Qsci


class CodeText(Qsci.QsciScintilla):

    # According to docs, The 0-7 are normally used by lexers
    _CURRENT_POSITION_INDICATOR = 8
    _ERROR_INDICATOR = 9

    key_during_visualisation = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_settings()
        self.configure_styles()

        self.setLexer(None)

        self._last_command_position = (0, 0)
        self._error_locations = set()
        self._during_visualisation = False

    def init_settings(self):
        self.setEolMode(Qsci.QsciScintilla.SC_EOL_LF)
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

        self.setScrollWidth(1)

    def configure_styles(self):
        self.setCaretLineBackgroundColor(QtGui.QColor(245, 245, 245))
        self.setIndentationGuidesBackgroundColor(QtGui.QColor(211, 211, 211))
        self.setIndentationGuidesForegroundColor(QtGui.QColor(211, 211, 211))

        self.indicatorDefine(self.FullBoxIndicator, self._CURRENT_POSITION_INDICATOR)
        self.setIndicatorDrawUnder(True, self._CURRENT_POSITION_INDICATOR)
        self.setIndicatorForegroundColor(
            QtGui.QColor('grey'), indicatorNumber=self._CURRENT_POSITION_INDICATOR
        )
        self.setIndicatorOutlineColor(
            QtGui.QColor('grey'), indicatorNumber=self._CURRENT_POSITION_INDICATOR
        )

        self.indicatorDefine(self.FullBoxIndicator, self._ERROR_INDICATOR)
        self.setIndicatorDrawUnder(True, self._ERROR_INDICATOR)
        self.setIndicatorForegroundColor(
            QtGui.QColor('yellow'), indicatorNumber=self._ERROR_INDICATOR
        )
        self.setIndicatorOutlineColor(
            QtGui.QColor('yellow'), indicatorNumber=self._ERROR_INDICATOR
        )

    def set_lexer(self, lexer):
        self.setLexer(lexer(self))

    def highlight_position(self, position, chars):
        self.SendScintilla(self.SCI_SETINDICATORCURRENT, self._CURRENT_POSITION_INDICATOR)
        self.remove_highlight_position()
        self.SendScintilla(self.SCI_INDICATORFILLRANGE, position, chars)
        self._last_command_position = (position, chars)

    def remove_highlight_position(self):
        self.SendScintilla(self.SCI_SETINDICATORCURRENT, self._CURRENT_POSITION_INDICATOR)
        self.SendScintilla(self.SCI_INDICATORCLEARRANGE, *self._last_command_position)
        self._last_command_position = (0, 0)

    def highlight_error(self, position, chars):
        self.SendScintilla(self.SCI_SETINDICATORCURRENT, self._ERROR_INDICATOR)
        self.SendScintilla(self.SCI_INDICATORFILLRANGE, position, chars)
        self._error_locations.add((position, chars))

    def remove_errors(self):
        if not self._error_locations:
            return
        self.SendScintilla(self.SCI_SETINDICATORCURRENT, self._ERROR_INDICATOR)
        for position, chars in self._error_locations:
            self.SendScintilla(self.SCI_INDICATORCLEARRANGE, position, chars)
        self._error_locations = set()

    def keyPressEvent(self, event):
        if self._during_visualisation:
            self.key_during_visualisation.emit()
        return super().keyPressEvent(event)

    def visualisation_started(self):
        self.setReadOnly(True)
        self._during_visualisation = True

    def visualisation_stopped(self):
        self.setReadOnly(False)
        self._during_visualisation = False
        self.remove_highlight_position()
        self.remove_errors()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    code_text = CodeText()
    window.setCentralWidget(code_text)
    window.show()
    app.exec_()
