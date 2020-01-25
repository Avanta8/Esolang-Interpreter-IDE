import enum

from PyQt5 import QtCore, QtGui, QtWidgets


class DropLocations(enum.Enum):
    NONE = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    MIDDLE = enum.auto()
    TABBAR = enum.auto()


class NotebookSplitter(QtWidgets.QSplitter):

    DIRECTION_TO_ORIENTATION = {
        DropLocations.TOP: QtCore.Qt.Vertical,
        DropLocations.BOTTOM: QtCore.Qt.Vertical,
        DropLocations.LEFT: QtCore.Qt.Horizontal,
        DropLocations.RIGHT: QtCore.Qt.Horizontal,
    }

    DIRECTION_TO_NEXT_INDEX = {
        DropLocations.TOP: 0,
        DropLocations.BOTTOM: 1,
        DropLocations.LEFT: 0,
        DropLocations.RIGHT: 1,
    }

    def __init__(self, *args, _add_tabs=False):
        super().__init__(*args)

        self.setChildrenCollapsible(False)
        self.setHandleWidth(1)

        if _add_tabs:
            self.addWidget(NotebookTabWidget(_add_tabs=True))
            self.addWidget(NotebookTabWidget(_add_tabs=True))
            self.addWidget(NotebookTabWidget(_add_tabs=True))

    def insert_tab(self, notebook, location, drag_info):
        insert_orientation = self.DIRECTION_TO_ORIENTATION[location]
        current_index = self.indexOf(notebook)
        if insert_orientation == self.orientation():
            next_index = current_index + self.DIRECTION_TO_NEXT_INDEX[location]
            new_tabwidget = NotebookTabWidget()
            new_tabwidget.add_from_drag_info(drag_info)
            self.insertWidget(next_index, new_tabwidget)
        else:
            if self.count() <= 1:
                self.setOrientation(insert_orientation)
                self.insert_tab(notebook, location, drag_info)
            else:
                new_splitter = NotebookSplitter()
                new_splitter.addWidget(notebook)
                new_splitter.insert_tab(notebook, location, drag_info)
                self.insertWidget(current_index, new_splitter)

    def childEvent(self, event):
        if event.removed() and self.count() == 0:
            self.deleteLater()
        return super().childEvent(event)


class NotebookTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None, _add_tabs=False):
        super().__init__(parent=parent)
        self.setAcceptDrops(True)

        self.setTabBar(NotebookTabBar(self))
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)

        self._rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self._stackedwidget = self.findChild(QtWidgets.QStackedWidget)

        if _add_tabs:
            self.addTab(QtWidgets.QTextEdit(f'{id(self)}: page1', self), 'Page 1')
            self.addTab(QtWidgets.QTextEdit(f'{id(self)}: page2', self), 'Page 2')
            self.addTab(QtWidgets.QTextEdit(f'{id(self)}: page3', self), 'Page 3')

    def close_tab(self, index):
        widget = self.widget(index)
        self.removeTab(index)
        widget.deleteLater()

    def dragEnterEvent(self, event):
        if self._is_valid_drag_event(event):
            event.accept()

    def dragMoveEvent(self, event):
        location, rect = self._check_drag_in_page(event.pos())
        if location is DropLocations.NONE:
            location, rect, index = self._check_drag_in_tabbar(event.pos())

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
        """Check if `pos` is within the current page. If it is, return
        the location along with the rect for the rubberband. Otherwise,
        return DropLocations.NONE, None.

            - Return: (DropLocation, (x, y, w, h))
                      (DropLocation.NONE, None)
        """

        # Check whether `pos` is within the page
        if not self._stackedwidget.geometry().contains(pos):
            return DropLocations.NONE, None

        # Map `pos` to relative to the page
        pos_in_widget = self._stackedwidget.mapFrom(self, pos)
        wx, wy = pos_in_widget.x(), pos_in_widget.y()

        # Where (0, 0) in the page is on the tabwidget
        offset = self._stackedwidget.mapTo(self, QtCore.QPoint(0, 0))
        dx, dy = offset.x(), offset.y()

        width = self._stackedwidget.width()
        height = self._stackedwidget.height()

        if wy < height / 4:
            return DropLocations.TOP, (dx, dy, width, height / 4)
        elif wy > height * 3 / 4:
            return DropLocations.BOTTOM, (dx, dy + height * 3 / 4, width, height / 4)
        elif wx < width / 4:
            return DropLocations.LEFT, (dx, dy, width / 4, height)
        elif wx > width * 3 / 4:
            return DropLocations.RIGHT, (dx + width * 3 / 4, dy, width / 4, height)
        # return DropLocations.MIDDLE, None
        return DropLocations.MIDDLE, (dx, dy, width, height)

    def _check_drag_in_tabbar(self, pos):
        """Check if `pos` is within the tabbar. If it is, return
        the location, the rect for the rubberband, and the index is would
        be inserted in. Otherwise, return DropLocations.NONE, None, -1.

            - Return: (DropLocation, (x, y, w, h), index)
            - Return: (DropLocation.None, None, -1)
        """

        tabbar = self.tabBar()
        pos_in_widget = tabbar.mapFrom(self, pos)
        wx, wy = pos_in_widget.x(), pos_in_widget.y()

        offset = tabbar.mapTo(self, QtCore.QPoint(0, 0))
        dx, dy = offset.x(), offset.y()

        # Check if `pos` is within the tabbar
        # Note: the width of the tabbar is only the visible width, so if the
        #   drag was at the end of the tabbar, it would be outside of the geometry
        #   of the tabbar. However, we still want to record this, so we only check the height
        if not 0 <= wy <= tabbar.height():
            return DropLocations.NONE, None, -1

        for i in range(self.count()):
            rect = tabbar.tabRect(i)
            tx, ty, tw, th = rect.getRect()

            if wx < tx + tw / 2:
                # If `pos` is within the first half of that tab
                insert_index = i
                break
            elif wx < tx + tw:
                # If `pos` is within the second half of that tab
                insert_index = i + 1
                break
        else:
            # `pos` must be longer than the visible tabs
            insert_index = self.count()

        # Determine the rect for the rubberband
        prev_rect = tabbar.tabRect(insert_index - 1)
        px, py, pw, ph = prev_rect.getRect()

        if insert_index < self.count():
            # Dragged within the current tabs
            next_rect = tabbar.tabRect(insert_index)
            nx, ny, nw, nh = next_rect.getRect()

            # Make the rubberband appear at the second half of the previous tab and
            # the first half of the next tab
            rubberband_rect = dx + px + pw / 2, dy, pw / 2 + nw / 2, tabbar.height()
        else:
            # Dragged longer than the current tabs
            # Make the width of the rubberband the same length as the last tab
            rubberband_rect = dx + px + pw / 2, dy, pw, tabbar.height()

        return DropLocations.TABBAR, rubberband_rect, insert_index

    def dropEvent(self, event):
        self._rubberband.hide()
        drag_info = event.source().drag_info
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

        location, index = self._get_drop_location(event.pos())
        if location is DropLocations.TABBAR:
            self.insert_from_drag_info(index, drag_info)
        elif location is DropLocations.MIDDLE:
            self.add_from_drag_info(drag_info)
        else:
            print('splitter', location)
            self.parent().insert_tab(self, location, drag_info)

    def _get_drop_location(self, pos):
        """Return the correct drop location for pos. If the drop location is the
        tabbar, return the index it was dropped at; otherwise, return -1 as the drop location."""
        location, _, index = self._check_drag_in_tabbar(pos)
        if index == self.count():
            # If inserting to the end of the tabs, just add it instead.
            location = DropLocations.MIDDLE
        if location is DropLocations.NONE:
            location, _ = self._check_drag_in_page(pos)
        return location, index

    def _is_valid_drag_event(self, event):
        """Return if the QDropEvent `event` is valid for this widget."""
        return isinstance(event.source(), NotebookTabBar)

    def insert_from_drag_info(self, index, drag_info):
        if self.indexOf(drag_info.widget) != index:
            # Only add if inserted into a different index
            self.insertTab(index, drag_info.widget, drag_info.tabname)

    def add_from_drag_info(self, drag_info):
        if self.indexOf(drag_info.widget) == -1:
            # Only add if that tab is not currently in this tabwidget
            self.addTab(drag_info.widget, drag_info.tabname)

    def tabInserted(self, index):
        """Called when tab is added or inserted.
        Set the current tab to that tab."""
        self.setCurrentIndex(index)

    def tabRemoved(self, index):
        """Called when tab is removed."""
        if self.count() == 0:
            self.deleteLater()


class NotebookTabBar(QtWidgets.QTabBar):
    def __init__(self, tabwidget=None):
        super().__init__(tabwidget)

        self.setAcceptDrops(True)

        self.drag_info = DragInfo()
        self._tabwidget = tabwidget

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            tab_index = self.tabAt(event.pos())
            self.drag_info = DragInfo(event.pos(), tab_index,
                                      self._tabwidget.widget(tab_index),
                                      self.tabText(tab_index))

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Pressed buttons don't include lmb, or tab not selected at start of drag, or
        # not reached min drag distance.
        if (event.buttons() | QtCore.Qt.LeftButton) != event.buttons() \
                or self.drag_info.tab_index == -1 \
                or QtCore.QLineF(event.pos(), self.drag_info.initial_pos).length() < 10:
            return super().mouseMoveEvent(event)

        tab_rect = self.tabRect(self.drag_info.tab_index)

        pixmap = QtGui.QPixmap(tab_rect.size())
        self.render(pixmap, sourceRegion=QtGui.QRegion(tab_rect))
        mime_data = QtCore.QMimeData()
        cursor = QtGui.QCursor(QtCore.Qt.OpenHandCursor)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - self.drag_info.initial_pos)
        drag.setDragCursor(cursor.pixmap(), QtCore.Qt.MoveAction)

        drag.exec_(QtCore.Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_info = DragInfo()

        return super().mouseReleaseEvent(event)


class DragInfo:
    def __init__(self, initial_pos=None, tab_index=-1, widget=None, tabname=None):
        super().__init__()

        self.initial_pos = initial_pos
        self.tab_index = tab_index
        self.widget = widget
        self.tabname = tabname


def main():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    notebook = NotebookSplitter(_add_tabs=True)
    window.setCentralWidget(notebook)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
