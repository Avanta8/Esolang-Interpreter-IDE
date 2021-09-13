import os

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
from editor_area import EditorNotebook

from file_info import FileInfo

# Look at: https://doc.qt.io/qtforpython/overviews/model-view-programming.html#using-views-with-an-existing-model
# for file system view


class IDE(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

        self._file_dialog_filter = 'All Files (*);;Text Files (*.txt);;Brainfuck (*.b)'

        self.show()

    def init_widgets(self):
        self.setGeometry(300, 200, 1280, 720)

        menus = {
            'File': (
                (('New', self), ('Ctrl+N',), ('New file',), (self.file_new,)),
                (('Open', self), ('Ctrl+O',), ('Open file',), (self.file_open,)),
                (('Save', self), ('Ctrl+S',), ('Save file',), (self.file_save,)),
                (('Save As', self), ('Ctrl+Shift+S',), ('Save as',), (self.file_saveas,)),
            ),
            'Run': (
                (('Run code', self), ('Ctrl+B',), ('Run code',), (self.run_code,)),
                (
                    ('Open visualiser', self),
                    ('Ctrl+Shift+B',),
                    ('Visualise run code',),
                    (self.open_visualier,),
                ),
            ),
        }

        menubar = self.menuBar()
        for name, actions in menus.items():
            menu = menubar.addMenu(name)
            for action, shortcut, statustip, connect in actions:
                action = QtWidgets.QAction(*action)
                action.setShortcut(*shortcut)
                action.setStatusTip(*statustip)
                action.triggered.connect(*connect)
                menu.addAction(action)

        self.statusBar()

        self.editor_notebook = EditorNotebook(self)
        self.setCentralWidget(self.editor_notebook)

    def file_new(self):
        self.create_new_page(FileInfo.from_empty())

    def file_open(self):
        filepath, extension = QtWidgets.QFileDialog.getOpenFileName(
            self, filter=self._file_dialog_filter
        )
        if not filepath:
            return

        fileinfo = FileInfo.from_filepath(filepath)
        self.create_new_page(fileinfo, fileinfo.read())

    def file_save(self):
        fileinfo = self.editor_notebook.get_current_fileinfo()
        if fileinfo is None:  # No currently selected tab
            return

        if fileinfo.is_empty():
            self.file_saveas()
        else:
            fileinfo.write(self.editor_notebook.get_current_text())

    def file_saveas(self):
        if self.editor_notebook.current_tabwidget() is None:
            return

        filepath, extension = QtWidgets.QFileDialog.getSaveFileName(
            self, filter=self._file_dialog_filter
        )

        if not filepath:
            return

        fileinfo = FileInfo.from_filepath(filepath)
        self.editor_notebook.set_current_fileinfo(fileinfo)
        self.file_save()

    def run_code(self):
        self.editor_notebook.open_code_runner()

    def open_visualier(self):
        self.editor_notebook.open_visualiser()

    def create_new_page(self, fileinfo, text=''):
        self.editor_notebook.new_page(fileinfo, text)


"""
TODO:
- Show when a file has changed. (star on top)
"""
