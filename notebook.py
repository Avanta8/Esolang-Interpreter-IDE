"""
Based on this StackOverflow question - https://stackoverflow.com/questions/46392463/drag-and-drop-a-tab-from-a-qtabbar-to-other-qtabbar-in-a-splitted-widget-pyqt-qt

I should subclass the QTabBar and catch the mousePressEvent there, so
I can bind onto the left mouse button.
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.tabBar().setMouseTracking(True)
        self.setMouseTracking(True)

        self.addTab(QtWidgets.QWidget(self), 'Page 1')
        self.addTab(QtWidgets.QWidget(self), 'Page 2')
        self.addTab(QtWidgets.QMainWindow(self), 'Page 3')

    # def mousePressEvent(self, event):
    #     if event.buttons() == QtCore.Qt.RightButton:
    #         self.last_right_pressed_pos = event.pos()
    #     else:
    #         super().mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    #     tabbar = self.tabBar()
    #     global_pos = self.mapToGlobal(event.pos())
    #     pos_in_tab = tabbar.mapFromGlobal(global_pos)
    #     tab_index = tabbar.tabAt(pos_in_tab)

    #     # Make sure that the tab has already been dragged a certain length
    #     if event.buttons() == QtCore.Qt.RightButton and tab_index != -1 \
    #             and QtCore.QLineF(event.pos(), self.last_right_pressed_pos).length() > 10:
    #         tabbar.dragged_content = self.widget(tab_index)
    #         tabbar.dragged_tabname = self.tabText(tab_index)
    #         tab_rect = tabbar.tabRect(tab_index)

    #         pixmap = QtGui.QPixmap(tab_rect.size())
    #         tabbar.render(pixmap, sourceRegion=QtGui.QRegion(tab_rect))
    #         mime_data = QtCore.QMimeData()
    #         cursor = QtGui.QCursor(QtCore.Qt.OpenHandCursor)

    #         drag = QtGui.QDrag(tabbar)
    #         drag.setMimeData(mime_data)
    #         drag.setPixmap(pixmap)
    #         drag.setHotSpot(event.pos() - pos_in_tab)
    #         drag.setDragCursor(cursor.pixmap(), QtCore.Qt.MoveAction)

    #         drag.exec_(QtCore.Qt.MoveAction)
    #     else:
    #         super().mouseMoveEvent(event)

    # def dragEnterEvent(self, event):
    #     if self.valid_drag_event(event):
    #         event.accept()

    # def dragLeaveEvent(self, event):
    #     event.accept()

    # def dropEvent(self, event):
    #     if not self.valid_drag_event(event):
    #         return

    #     tabbar = event.source()
    #     event.accept()
    #     event.setDropAction(QtCore.Qt.MoveAction)
    #     self.addTab(tabbar.dragged_content, tabbar.dragged_tabname)

    # def valid_drag_event(self, event):
    #     source = event.source()
    #     return source is not None and hasattr(source, 'dragged_content')


class Notebook(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.create_widgets()

    def create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.splitter.addWidget(TabWidget(self))
        self.splitter.addWidget(TabWidget(self))

        self.splitter.mouseMoveEvent = lambda e: print('splitter mouse move entet')

    def add_tab(self, widget):
        pass


def main():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    notebook = Notebook()
    window.setCentralWidget(notebook)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
