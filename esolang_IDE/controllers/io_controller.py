import enum
from typing import NamedTuple, Callable

from PyQt5 import QtWidgets

from .page_controller import PageController

from esolang_IDE.editor_page import EditorPage
from esolang_IDE.notebook import Notebook
from esolang_IDE.file_info import FileInfo
from esolang_IDE.main_window import IDE


class _PageInfo(NamedTuple):
    controller: PageController
    fileinfo: FileInfo


class _FileOperation(enum.Enum):
    new = enum.auto()
    save = enum.auto()
    open = enum.auto()
    saveas = enum.auto()


class _RunOperation(enum.Enum):
    run = enum.auto()
    visualiser = enum.auto()


class _OperationHandler:

    _op2fn: dict[enum.Enum, Callable]

    def __init__(self, notebook: Notebook, pages: dict[EditorPage, _PageInfo]):
        self.notebook = notebook
        self.pages = pages

    def handle(self, operation: enum.Enum):
        return self._op2fn[operation]()


class _FileOperationHandler(_OperationHandler):
    def __init__(self, notebook: Notebook, pages: dict[EditorPage, _PageInfo]):
        self.notebook = notebook
        self.pages = pages

        self._op2fn = {
            _FileOperation.new: self._new,
            _FileOperation.save: self._save,
            _FileOperation.open: self._open,
            _FileOperation.saveas: self._saveas,
        }

        self._file_dialog_filter = 'All Files (*);;Text Files (*.txt);;Brainfuck (*.b)'

    def _new(self):
        self._create_new_page(FileInfo.from_empty())

    def _open(self):
        filepath, extension = QtWidgets.QFileDialog.getOpenFileName(
            filter=self._file_dialog_filter
        )
        if not filepath:
            return

        fileinfo = FileInfo.from_filepath(filepath)
        self._create_new_page(fileinfo, fileinfo.read())

    def _save(self):
        current_page = self.notebook.current_page()
        if current_page is None:
            return

        page_controller, fileinfo = self.pages[current_page]
        if fileinfo.is_empty():
            self._saveas()
        else:
            fileinfo.write(page_controller.get_text())
            self._update_pagename(current_page)

    def _saveas(self):
        current_page = self.notebook.current_page()
        if current_page is None:
            return

        filepath, extension = QtWidgets.QFileDialog.getSaveFileName(
            filter=self._file_dialog_filter
        )

        if not filepath:
            return

        page_controller, fileinfo = self.pages[current_page]
        fileinfo.update_from_filepath(filepath)
        page_controller.set_filetype(fileinfo.filetype)
        self._save()

    def _create_new_page(self, fileinfo: FileInfo, text=''):
        page = EditorPage()
        self.notebook.add_tab_to_current(page, fileinfo.filename or 'Untitled')

        page_controller = PageController(editor_page=page, text=text)
        page_controller.set_filetype(fileinfo.filetype)
        page_controller.text_changed.connect(self._page_text_changed)

        self.pages[page] = _PageInfo(page_controller, fileinfo)

    def _page_text_changed(self, page):
        fileinfo = self.pages[page].fileinfo
        if not fileinfo.changed:
            fileinfo.changed = True
            self._update_pagename(page)

    def _update_pagename(self, page):
        fileinfo = self.pages[page].fileinfo
        self.notebook.set_page_tab_text(
            page, f'{"*. " if fileinfo.changed else ""}{fileinfo.filename or "Untitled"}'
        )


class _RunOperationHandler(_OperationHandler):
    def __init__(self, notebook: Notebook, pages: dict[EditorPage, _PageInfo]):
        super().__init__(notebook, pages)

        self._op2fn = {
            _RunOperation.run: self._run_code,
            _RunOperation.visualiser: self._open_visualier,
        }

    def _run_code(self):
        page = self.notebook.current_page()
        if page is None:
            return

        self.pages[page].controller.run_code()

    def _open_visualier(self):
        page = self.notebook.current_page()
        if page is None:
            return

        self.pages[page].controller.open_visualiser()


class IOController:
    def __init__(self):

        self.notebook = Notebook()
        self.notebook.page_closed.connect(self._page_closed)

        self.pages: dict[EditorPage, _PageInfo] = {}

        self.file_handler = _FileOperationHandler(self.notebook, self.pages)
        self.run_handler = _RunOperationHandler(self.notebook, self.pages)

        self.init_mainwindow()

    def init_mainwindow(self):
        file_handle = lambda op: (lambda: self.file_handler.handle(op))
        run_handle = lambda op: (lambda: self.run_handler.handle(op))

        self.ide = IDE(
            menu_layout={
                'File': (
                    ('New', 'Ctrl+N', 'New file', file_handle(_FileOperation.new)),
                    ('Open', 'Ctrl+O', 'Open file', file_handle(_FileOperation.open)),
                    ('Save', 'Ctrl+S', 'Save file', file_handle(_FileOperation.save)),
                    (
                        'Save As',
                        'Ctrl+Shift+S',
                        'Save as',
                        file_handle(_FileOperation.saveas),
                    ),
                ),
                'Run': (
                    ('Run code', 'Ctrl+B', 'Run code', run_handle(_RunOperation.run)),
                    (
                        'Open visualiser',
                        'Ctrl+Shift+B',
                        'Visualise execution',
                        run_handle(_RunOperation.visualiser),
                    ),
                ),
            }
        )
        self.ide.setGeometry(300, 200, 1280, 720)
        self.ide.setCentralWidget(self.notebook)

    def _page_closed(self, page):
        # Clean up reference
        self.pages.pop(page)
