from PyQt5 import QtCore, QtWidgets

from editor_page import EditorPage
from notebook import Notebook
from file_info import FileInfo


class IOController:
    def __init__(self, ide):
        self.ide = ide

        self.notebook = Notebook(self.ide)
        self.notebook.page_closed.connect(self._page_closed)

        self.pages = {}

        self._file_dialog_filter = 'All Files (*);;Text Files (*.txt);;Brainfuck (*.b)'

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

        fileinfo = self.pages[current_page]
        if fileinfo.is_empty():
            self.file_saveas()
        else:
            fileinfo.write(current_page.get_text())
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
    
        fileinfo = self.pages[current_page]
        fileinfo.update_from_filepath(filepath)
        current_page.set_filetype(fileinfo.filetype)
        self.file_save()

    def run_code(self):
        page = self.notebook.current_page()
        if page is None:
            return
        
        page.open_code_runner()

    def open_visualier(self):
        page = self.notebook.current_page()
        if page is None:
            return
        
        page.open_visualiser()

    def create_new_page(self, fileinfo: FileInfo, text=''):
        page = EditorPage(fileinfo.filetype, text)
        self.notebook.add_tab_to_current(page, fileinfo.filename or 'Untitled')
        self.pages[page] = fileinfo
        page.text_changed.connect(self._page_text_changed)

    def get_main_widget(self):
        """Return the widget that should be set as the central widget of the main window."""
        return self.notebook

    def _page_closed(self, page):
        # Clean up reference
        self.pages.pop(page)

    def _page_text_changed(self, page):
        fileinfo = self.pages[page]
        if not fileinfo.changed:
            fileinfo.changed = True
            self._update_pagename(page)

    def _update_pagename(self, page):
        fileinfo = self.pages[page]
        self.notebook.set_page_tab_text(page, f'{"*. " if fileinfo.changed else ""}{fileinfo.filename}')
