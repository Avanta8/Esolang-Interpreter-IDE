from PyQt5 import QtCore
from .visualiser_controller import VisualiserController
from .runner_controller import RunnerController

from editor_page import EditorPage
from code_text import CodeText
from code_runner import CodeRunner


class PageController(QtCore.QObject):

    text_changed = QtCore.pyqtSignal(QtCore.QObject)

    def __init__(self, editor_page: EditorPage, text: str = ''):
        super().__init__()

        # TODO:
        # Perhaps disable the visualiser and code runner fileinfo.filetype is None.

        self._editor_page = editor_page

        self._editor_page.code_runner_closed.connect(self.code_runner_closed)
        self._editor_page.visualiser_closed.connect(self.visualiser_closed)

        self._code_text = self._editor_page.get_code_text()
        code_runner = self._editor_page.get_code_runner()
        visualiser = self._editor_page.get_visualiser()

        self._visualiser_controller = VisualiserController(self._code_text, visualiser)
        self._runner_controller = RunnerController(self._code_text, code_runner)

        self._code_text.textChanged.connect(self._code_text_changed)

        if text:
            self._code_text.setText(text)

    def run_code(self):
        self._editor_page.open_code_runner()
        self._runner_controller.run_code()

    def open_visualiser(self):
        self._editor_page.open_visualiser()

    def visualiser_closed(self):
        self._visualiser_controller.closed()

    def code_runner_closed(self):
        self._runner_controller.interrupt()

    def set_filetype(self, filetype):
        self._code_text.set_filetype(filetype)
        self._runner_controller.set_filetype(filetype)
        self._visualiser_controller.set_filetype(filetype)

    def get_text(self):
        return self._code_text.text()

    def get_page(self):
        return self._editor_page

    @QtCore.pyqtSlot()
    def _code_text_changed(self):
        self.text_changed.emit(self._editor_page)
