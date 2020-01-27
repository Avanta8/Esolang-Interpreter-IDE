import os

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes
from editor_area import EditorNotebook


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
                (('Open visualiser', self), ('Ctrl+Shift+B',), ('Visualise run code',), (self.open_visualier,)),
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
        # self.editor_notebook.new_page()
        self.create_new_page()

    def file_open(self):
        print('file_open')
        filepath, extension = QtWidgets.QFileDialog.getOpenFileName(self, filter=self._file_dialog_filter)
        if not filepath:
            return

        text = self._read_file(filepath)
        self.create_new_page(*self._parse_filepath(filepath), text)

    def file_save(self):
        print('file_save')
        current_file_info = self.editor_notebook.get_current_file_info()
        if current_file_info is None:
            print('no current file')
            return

        filepath, _ = current_file_info
        if filepath is None:
            self.file_saveas()
        else:
            self._write_file(filepath, self.editor_notebook.get_current_text())

    def file_saveas(self):
        print('file_saveas')
        if self.editor_notebook.current_tabwidget() is None:
            print('no current tabwidget')
            return

        filepath, extension = QtWidgets.QFileDialog.getSaveFileName(self, filter=self._file_dialog_filter)

        if not filepath:
            return

        self.editor_notebook.set_current_file_info(*self._parse_filepath(filepath))
        self.file_save()

    def run_code(self):
        print('run_code')
        self.editor_notebook.open_code_runner()

    def open_visualier(self):
        print('open_visualier')
        self.editor_notebook.open_visualiser()

    def create_new_page(self, filename=None, filepath=None, filetype=FileTypes.NONE, text=''):
        self.editor_notebook.new_page(filename=filename, filepath=filepath, filetype=filetype, text=text)

    @staticmethod
    def _read_file(filepath):
        """Read `filepath` and return the contents."""
        with open(filepath, 'r') as file:
            read = file.read()
        return read

    @staticmethod
    def _write_file(filepath, text):
        """Write `text` to `filepath`."""
        with open(filepath, 'w') as file:
            file.write(text)

    @staticmethod
    def _parse_filepath(filepath):
        """Return filename, filepath, filetype"""
        extension = os.path.splitext(filepath)[1]
        filetype = FileTypes.BRAINFUCK if extension == '.b' else FileTypes.NONE
        filename = os.path.basename(filepath)
        return filename, filepath, filetype


def main():
    app = QtWidgets.QApplication([])
    _ = IDE()
    app.exec_()


main()
