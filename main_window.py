from PyQt5 import QtCore, QtGui, QtWidgets

from editor_area import EditorNotebook


class IDE(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

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
        print('file_new')
        self.editor_notebook.new_page()

    def file_open(self):
        print('file_open')

    def file_save(self):
        print('file_save')

    def file_saveas(self):
        print('file_saveas')

    def run_code(self):
        print('run_code')

    def open_visualier(self):
        print('open_visualier')


def main():
    app = QtWidgets.QApplication([])
    _ = IDE()
    app.exec_()


main()
