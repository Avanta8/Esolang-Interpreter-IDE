from PyQt5 import QtWidgets, QtGui, Qsci


class CodeText(Qsci.QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.init_settings()
        self.configure_styles()

        self.setFont(QtGui.QFont('Source Code Pro', 10))

    def init_settings(self):
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


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    code_text = CodeText()
    window.setCentralWidget(code_text)
    window.show()
    app.exec_()
