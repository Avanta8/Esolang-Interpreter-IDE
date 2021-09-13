from PyQt5 import QtCore, QtGui, QtWidgets

from notebook import Notebook
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

    def __init__(self, fileinfo, text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO:
        # Perhaps disable the visualiser and code runner fileinfo.filetype is None.

        self.init_widgets()

        self.set_fileinfo(fileinfo)

        if text:
            self.code_text.setText(text)

        self._text_has_changed = False

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

    def set_fileinfo(self, fileinfo):
        self.fileinfo = fileinfo

        self.code_text.set_filetype(fileinfo.filetype)
        self.visualiser.set_filetype(fileinfo.filetype)
        self.code_runner.set_filetype(fileinfo.filetype)

    def get_fileinfo(self):
        return self.fileinfo

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

    def _code_text_changed(self):
        if self._text_has_changed:
            return

        self.text_changed.emit(self)
        self._text_has_changed = True

    def code_text_unchanged(self):
        self._text_has_changed = False


class EditorNotebook(Notebook):
    def new_page(self, fileinfo, text):
        page = EditorPage(fileinfo, text)
        self.add_tab_to_current(page, fileinfo.filename or 'Untitled')

        page.text_changed.connect(self._page_text_changed)

    def _page_text_changed(self, page):
        filename = page.get_fileinfo().filename
        self.set_page_tab_text(page, f'*. {filename}')

    def set_current_fileinfo(self, fileinfo):
        tabwidget = self.current_tabwidget()
        if tabwidget is None:
            return

        index = tabwidget.currentIndex()
        tabwidget.setTabText(index, fileinfo.filename)
        self.current_page().set_fileinfo(fileinfo)

    def get_current_fileinfo(self):
        page = self.current_page()
        if page is None:
            return None

        # This is assuming that we always get the fileinfo for saving the file,
        # which means that we can mark the page as not changed (remove the
        # asterisk from the tab bar text).
        # However, if in the future, this is method accessed for other reasons,
        # this should be changed.
        page.code_text_unchanged()
        self.set_page_tab_text(page, page.get_fileinfo().filename)

        return page.get_fileinfo()

    def get_current_text(self):
        page = self.current_page()
        if page is None:
            return None
        return page.get_text()

    def open_visualiser(self):
        page = self.current_page()
        if page is None:
            return
        page.open_visualiser()

    def open_code_runner(self):
        page = self.current_page()
        if page is None:
            return
        page.open_code_runner()
