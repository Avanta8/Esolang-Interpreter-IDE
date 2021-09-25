from typing import NamedTuple

from PyQt5 import QtCore, QtWidgets

from .page_controller import PageController

from esolang_IDE.editor_page import EditorPage
from esolang_IDE.notebook import Notebook
from esolang_IDE.file_info import FileInfo
from esolang_IDE.main_window import IDE


class _PageInfo(NamedTuple):
    controller: PageController
    fileinfo: FileInfo


class IOController:
    def __init__(self):

        self.notebook = Notebook()
        self.notebook.page_closed.connect(self._page_closed)

        self.pages: dict[EditorPage, _PageInfo] = {}

        self._file_dialog_filter = 'All Files (*);;Text Files (*.txt);;Brainfuck (*.b)'

        self.init_mainwindow()

    def init_mainwindow(self):
        self.ide = IDE(
            menu_layout={
                'File': (
                    ('New', 'Ctrl+N', 'New file', self.file_new),
                    ('Open', 'Ctrl+O', 'Open file', self.file_open),
                    ('Save', 'Ctrl+S', 'Save file', self.file_save),
                    ('Save As', 'Ctrl+Shift+S', 'Save as', self.file_saveas),
                ),
                'Run': (
                    ('Run code', 'Ctrl+B', 'Run code', self.run_code),
                    (
                        'Open visualiser',
                        'Ctrl+Shift+B',
                        'Visualise execution',
                        self.open_visualier,
                    ),
                ),
            }
        )
        self.ide.setGeometry(300, 200, 1280, 720)
        self.ide.setCentralWidget(self.notebook)

    def file_new(self):
        self.create_new_page(FileInfo.from_empty())

    def file_open(self):
        filepath, extension = QtWidgets.QFileDialog.getOpenFileName(
            filter=self._file_dialog_filter
        )
        if not filepath:
            return

        fileinfo = FileInfo.from_filepath(filepath)
        self.create_new_page(fileinfo, fileinfo.read())

    def file_save(self):
        current_page = self.notebook.current_page()
        if current_page is None:
            return

        page_controller, fileinfo = self.pages[current_page]
        if fileinfo.is_empty():
            self.file_saveas()
        else:
            fileinfo.write(page_controller.get_text())
            self._update_pagename(current_page)

    def file_saveas(self):
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
        self.file_save()

    def run_code(self):
        page = self.notebook.current_page()
        if page is None:
            return

        self.pages[page].controller.run_code()

    def open_visualier(self):
        page = self.notebook.current_page()
        if page is None:
            return

        self.pages[page].controller.open_visualiser()

    def create_new_page(self, fileinfo: FileInfo, text=''):
        page = EditorPage()
        self.notebook.add_tab_to_current(page, fileinfo.filename or 'Untitled')

        page_controller = PageController(editor_page=page, text=text)
        page_controller.set_filetype(fileinfo.filetype)
        page_controller.text_changed.connect(self._page_text_changed)

        self.pages[page] = _PageInfo(page_controller, fileinfo)

    def _page_closed(self, page):
        # Clean up reference
        self.pages.pop(page)

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
