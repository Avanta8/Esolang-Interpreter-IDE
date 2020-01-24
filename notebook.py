from PyQt5 import QtCore, QtGui, QtWidgets


class NotebookSplitter(QtWidgets.QSplitter):
    def __init__(self, *args):
        super().__init__(*args)

        self.setAcceptDrops(True)

        self.addWidget(NotebookTabWidget())
        self.addWidget(NotebookTabWidget())

    # def mouseMoveEvent(self, event):
    #     print('NotebookSplitter.mouseMoveEvent')
    #     return super().mouseMoveEvent(event)

    # def dragEnterEvent(self, event):
    #     print('NotebookSplitter.dragEnterEvent')


class NotebookTabWidget(QtWidgets.QTabWidget):
    _NONE = 0
    _TOP = 1
    _BOTTOM = 2
    _LEFT = 3
    _RIGHT = 4

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)
        # self.setMovable(True)
        # self.tabBar().setMouseTracking(True)
        # self.setMouseTracking(True)

        self.setTabBar(NotebookTabBar(self))
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)

        self._rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        self.addTab(QtWidgets.QWidget(self), 'Page 1')
        self.addTab(QtWidgets.QWidget(self), 'Page 2')
        self.addTab(QtWidgets.QMainWindow(self), 'Page 3')

    # def mouseMoveEvent(self, event):
    #     print('NotebookTabWidget.mouseMoveEvent')
    #     return super().mouseMoveEvent(event)

    def close_tab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()

    def dragEnterEvent(self, event):
        print('NotebookTabWidget.dragEnterEvent')
        if self._is_valid_drag_event(event):
            event.accept()

    def dragMoveEvent(self, event):
        print('dragMoveEvent')
        _, rect = self._check_drag_in_page(event.pos())
        if rect is None:
            # Now check if in tab area
            self._rubberband.hide()
        else:
            self._rubberband.setGeometry(*rect)
            self._rubberband.show()

    def dragLeaveEvent(self, event):
        self._rubberband.hide()
        event.accept()

    def _check_drag_in_page(self, pos):
        widget = self.currentWidget()

        if widget is None:
            return

        pos_in_widget = widget.mapFrom(self, pos)
        wx, wy = pos_in_widget.x(), pos_in_widget.y()

        offset = widget.mapTo(self, QtCore.QPoint(0, 0))
        dx, dy = offset.x(), offset.y()

        width = widget.width()
        height = widget.height()

        if widget.geometry().contains(pos_in_widget):
            if wy < height / 4:
                return self._TOP, (dx, dy, width, height / 4)
            elif wy > height * 3 / 4:
                return self._BOTTOM, (dx, dy + height * 3 / 4, width, height / 4)
            elif wx < width / 4:
                return self._LEFT, (dx, dy, width / 4, height)
            elif wx > width * 3 / 4:
                return self._RIGHT, (dx + width * 3 / 4, dy, width / 4, height)
        return self._NONE, None

    def dropEvent(self, event):
        self._rubberband.hide()
        drag_info = event.source()._drag_info
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

        location, _ = self._check_drag_in_page(event.pos())
        if location == self._NONE:
            self.addTab(drag_info.dragged_content, drag_info.dragged_tabname)
        else:
            # Now do something with the splitter window
            print(f'dropped in location {location}')

    def _is_valid_drag_event(self, event):
        return isinstance(event.source(), NotebookTabBar)

    def tabRemoved(self, index):
        if self.count() == 0:
            self.deleteLater()


class NotebookTabBar(QtWidgets.QTabBar):
    def __init__(self, tabwidget=None):
        super().__init__(tabwidget)

        self.setAcceptDrops(True)

        self._drag_info = None
        # self._drag_state = DragState()
        self._tabwidget = tabwidget

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            tab_index = self.tabAt(event.pos())
            self._drag_info = DragInfo(event.pos(), tab_index)

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # This doesn't quite work
        if (event.buttons() & QtCore.Qt.LeftButton) != event.buttons() \
                or self._drag_info.tab_index == -1 \
                or QtCore.QLineF(event.pos(), self._drag_info.pos).length() < 10:
            return super().mouseMoveEvent(event)

        self._drag_info.dragged_content = self._tabwidget.widget(self._drag_info.tab_index)
        self._drag_info.dragged_tabname = self.tabText(self._drag_info.tab_index)

        tab_rect = self.tabRect(self._drag_info.tab_index)

        pixmap = QtGui.QPixmap(tab_rect.size())
        self.render(pixmap, sourceRegion=QtGui.QRegion(tab_rect))
        mime_data = QtCore.QMimeData()
        cursor = QtGui.QCursor(QtCore.Qt.OpenHandCursor)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - self._drag_info.pos)
        drag.setDragCursor(cursor.pixmap(), QtCore.Qt.MoveAction)

        drag.exec_(QtCore.Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_info = DragInfo()

        return super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        print('NotebookTabBar.dragEnterEvent')


class DragInfo:
    def __init__(self, pos=None, tab_index=-1):
        super().__init__()

        self.pos = pos
        self.tab_index = tab_index
        self.dragged_content = None
        self.dragged_tabname = None


def main():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    notebook = NotebookSplitter()
    window.setCentralWidget(notebook)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
