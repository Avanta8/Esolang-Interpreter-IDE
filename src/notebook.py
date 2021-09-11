"""
Notebook that can handle tabs being dragged around to different locations.
Uses a hierarchy of QSplitters and QTabWidgets to store the tabs.

Todo:
    - When the tabbar is full and the drag is on the tabbar, then scroll the tabbar.
    - Allow icons to work with the tabs.
    - Allow user to specify splitter handle width.
    - Make it work with vertical orientation tabs.
    - Can drag the whole tabbar to drag the whole tabwidget
"""


import enum

from PyQt5 import QtCore, QtGui, QtWidgets


class _DropLocations(enum.Enum):
    NONE = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()
    MIDDLE = enum.auto()
    TABBAR = enum.auto()


class Notebook(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_tabwidget = None
        self._notebook_splitter = _NotebookSplitter(notebook=self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._notebook_splitter)
        self.setLayout(layout)

        QtWidgets.QApplication.instance().focusChanged.connect(self._focus_changed)

    def add_tab(self, *args, **kwargs):
        """Add a tab to the first notebook. Has the same overload as
        `QtWidgets.QTabWidget.addTab`."""
        # if self._notebook_splitter.count() == 0:
        #     self._notebook_splitter.addWidget(NotebookTabWidget())
        # self._notebook_splitter.widget(0).addTab(*args, **kwargs)
        self._notebook_splitter.addTab(*args, **kwargs)

    def add_tab_to_current(self, *args, **kwargs):
        """Add a tab to the current tabwidget. Has the same overload as
        `QtWidgets.QTabWidget.addTab`."""
        if self._current_tabwidget is not None:
            self._current_tabwidget.addTab(*args, **kwargs)
        else:
            self.add_tab(*args, **kwargs)

    def _focus_changed(self, old, new):
        """Called when the focus changes widget anywhere in the application.
        If `new` widget is a child of a `NotebookTabWidget`, then set that
        `NotebookTabWidget` to `self._current_tabwidget`.

        This may potetially be slow if `new` is nested deeply."""
        if self.isAncestorOf(new):
            while not isinstance(new, _NotebookTabWidget) or new.notebook != self:
                # Second check is incase of nested notebooks. Not actually tested yet.
                new = new.parent()
            self._current_tabwidget = new

    def current_tabwidget(self):
        """Return the current tabwidget."""
        return self._current_tabwidget

    def set_current_tabwidget(self, tabwidget):
        """Set the current tabwidget to `tabwidget`. If `tabwidget` is not
        in the notebook, then raise a `ValueError`."""
        if not isinstance(tabwidget, _NotebookTabWidget) or tabwidget.notebook is not self:
            raise ValueError('Notebook is not the parent of tabwidget')
        self._current_tabwidget = tabwidget

    def current_page(self):
        """Return current widget of the current tabwidget, or None if the current
        tabwidget is None."""
        if self._current_tabwidget is None:
            return None
        return self._current_tabwidget.currentWidget()


class _NotebookSplitter(QtWidgets.QSplitter):
    """Splitter that contains `NotebookTabWidget`s or other `ChildNotebookSplitter`s
    to display the hierarchy of tabwidgets."""

    DIRECTION_TO_ORIENTATION = {
        _DropLocations.TOP: QtCore.Qt.Vertical,
        _DropLocations.BOTTOM: QtCore.Qt.Vertical,
        _DropLocations.LEFT: QtCore.Qt.Horizontal,
        _DropLocations.RIGHT: QtCore.Qt.Horizontal,
    }

    DIRECTION_TO_NEXT_INDEX = {
        _DropLocations.TOP: 0,
        _DropLocations.BOTTOM: 1,
        _DropLocations.LEFT: 0,
        _DropLocations.RIGHT: 1,
    }

    def __init__(self, *args, notebook, **kwargs):
        super().__init__(*args, **kwargs)

        self.notebook = notebook

        self.setChildrenCollapsible(False)
        self.setHandleWidth(1)

    def addTab(self, *args, **kwargs):
        """Add the tab to the first widget in `self`. If `self` is
        empty, create a `NotebookTabWidget` and add it to that."""
        if self.count() == 0:
            self.addWidget(_NotebookTabWidget(notebook=self.notebook))
        self.widget(0).addTab(*args, **kwargs)

    def insert_tab(self, notebook, location, drag_info):
        """Insert a tab, called from `notebook`. Insert it at `location` relative
        to `notebook`. If neccesary (if the orientation of `location` is different from
        `self.orientation()` and `self.count()` >= 2), create a new `NotebookSplitter`
        and insert the tab in that.

        Arguments:
            `notebook`: `NotebookTabWidget`,
            `location`: `DropLocations`,
            `drag_info`: `DragInfo`
        """
        insert_orientation = self.DIRECTION_TO_ORIENTATION[location]
        current_index = self.indexOf(notebook)
        if insert_orientation == self.orientation():
            # No change necessary to the current orientation
            next_index = current_index + self.DIRECTION_TO_NEXT_INDEX[location]
            new_tabwidget = _NotebookTabWidget(notebook=self.notebook)
            new_tabwidget.add_from_drag_info(drag_info)
            self.insertWidget(next_index, new_tabwidget)
        else:
            # Different orientation required
            if self.count() < 2:
                # If there are only 1 or 0 inner widgets, so just swap `self.orientation()`
                self.setOrientation(insert_orientation)
                self.insert_tab(notebook, location, drag_info)
            else:
                # Need to create new NotebookSplitter with required orientation.
                # Add `notebook` to that splitter, and then insert the new tab.
                # Insert the new splitter in `self` replacing `Notebook`.
                new_splitter = _ChildNotebookSplitter(insert_orientation, notebook=self.notebook)
                new_splitter.replace_splitter_signal.connect(self._replace_splitter)
                new_splitter.addWidget(notebook)
                new_splitter.insert_tab(notebook, location, drag_info)
                self.insertWidget(current_index, new_splitter)

    def _replace_splitter(self, splitter):
        """Slot called by a child splitter when its count becomes 1.
        Replace that splitter with its only child."""
        index = self.indexOf(splitter)
        # The splitter may emit the signal multiple times.
        if index >= 0:
            self.replaceWidget(index, splitter.widget(0))
            splitter.hide()
            splitter.deleteLater()  # This may not be necessary


class _ChildNotebookSplitter(_NotebookSplitter):
    """Splitter used to display the hierarchy of tabwidgets. This splitter should
    never have less that 2 widgets displayed, apart from just after creation.
    Emit a `replace_splitter_signal` if a widget is removed and the count is 1.
    Delete `self` if a widget is removed and there are no other widgets being
    displayed by `self`."""
    replace_splitter_signal = QtCore.pyqtSignal(_NotebookSplitter)

    def childEvent(self, event):
        """If the event is a `QEvent.ChildRemoved` and the `count()` == 0, delete self.
        If the event is a `QEvent.ChildRemoved` and the `count()` == 1, then emit the signal
        to replace `self` with its only inner widget."""
        if event.removed() and self.count() == 0:
            self.hide()
            self.deleteLater()
        elif event.removed() and self.count() == 1:
            self.replace_splitter_signal.emit(self)

            # I could do this so it only emits the signal once.
            # self.blockSignals(True)
            # Then in `insert_tab`, check if the signals were originally
            # blocked before unblocking them.
        return super().childEvent(event)

    def insert_tab(self, *args, **kwargs):
        """Insert the tab like `NotebookSplitter`. However, prevent
        ALL signals from being emitted during the insertion."""
        self.blockSignals(True)
        super().insert_tab(*args, **kwargs)
        self.blockSignals(False)


class _NotebookTabWidget(QtWidgets.QTabWidget):
    """Tabwidget used by `NotebookSplitter`. Can handle drag events."""

    clicked = QtCore.pyqtSignal(QtWidgets.QTabWidget)

    def __init__(self, *args, notebook, **kwargs):
        super().__init__(*args, **kwargs)

        self.notebook = notebook
        self.clicked.connect(self.notebook.set_current_tabwidget)

        self.setAcceptDrops(True)

        self.setTabBar(_NotebookTabBar(self))
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.current_tab_changed)

        self._rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        self._stackedwidget = self.findChild(QtWidgets.QStackedWidget)  # Widget that displays the pages.

    def close_tab(self, index):
        """Called when the X is pressed on one of the tabs.
        Remove that tab and delete it."""
        widget = self.widget(index)
        self.removeTab(index)
        widget.hide()
        widget.deleteLater()

    def current_tab_changed(self, index):
        """Called when the current tab is changed. Set the current tabwidget in `self.notebook`
        to `self`."""
        self.clicked.emit(self)

    def dragEnterEvent(self, event):
        """Accept the drag event if it (the content) is valid."""
        if self._is_valid_drag_event(event):
            event.accept()

    def dragMoveEvent(self, event):
        """"Display the rubberband showing where the tab will end up
        if the drag was to be dropped."""
        location, rect, _ = self._get_drop_location(event.pos())

        if rect is None:
            self._rubberband.hide()
        else:
            self._rubberband.setGeometry(*rect)
            self._rubberband.show()

    def dragLeaveEvent(self, event):
        """Hide the rubberband, and accept the event."""
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
            return _DropLocations.NONE, None

        # Map `pos` to relative to the page
        pos_in_widget = self._stackedwidget.mapFrom(self, pos)
        wx, wy = pos_in_widget.x(), pos_in_widget.y()

        # Where (0, 0) in the page is on the tabwidget
        offset = self._stackedwidget.mapTo(self, QtCore.QPoint(0, 0))
        dx, dy = offset.x(), offset.y()

        width = self._stackedwidget.width()
        height = self._stackedwidget.height()

        if wx < width / 4:
            return _DropLocations.LEFT, (dx, dy, width / 4, height)
        if wx > width * 3 / 4:
            return _DropLocations.RIGHT, (dx + width * 3 / 4, dy, width / 4, height)
        if wy < height / 4:
            return _DropLocations.TOP, (dx, dy, width, height / 4)
        if wy > height * 3 / 4:
            return _DropLocations.BOTTOM, (dx, dy + height * 3 / 4, width, height / 4)
        return _DropLocations.MIDDLE, (dx, dy, width, height)

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
            return _DropLocations.NONE, None, -1

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
            # `pos` must be after the visible tabs
            insert_index = self.count()

        # Determine the rect for the rubberband
        prev_rect = tabbar.tabRect(insert_index - 1)
        px, py, pw, ph = prev_rect.getRect()

        if insert_index < self.count():
            # Drag within the current tabs
            next_rect = tabbar.tabRect(insert_index)
            nx, ny, nw, nh = next_rect.getRect()

            # Make the rubberband appear at the second half of the previous tab and
            # the first half of the next tab
            rubberband_rect = dx + px + pw / 2, dy, pw / 2 + nw / 2, tabbar.height()
        else:
            # Drag position after the current tabs
            # Make the width of the rubberband the same length as the last tab
            rubberband_rect = dx + px + pw / 2, dy, pw, tabbar.height()

        return _DropLocations.TABBAR, rubberband_rect, insert_index

    def dropEvent(self, event):
        """Hide the rubberband. Handle where the event should be dropped."""
        self._rubberband.hide()
        drag_info = event.source().drag_info
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

        location, _, index = self._get_drop_location(event.pos())
        if location is _DropLocations.TABBAR:
            self.insert_from_drag_info(index, drag_info)
        elif location is _DropLocations.MIDDLE or location is _DropLocations.NONE:
            self.add_from_drag_info(drag_info)
        else:
            self.parent().insert_tab(self, location, drag_info)

    def _get_drop_location(self, pos):
        """Return the correct drop location for pos, as well as the indication rect (for
        the rubberband), and the tab index it was dropped at. If the drop location is the
        tabbar, return the index it was dropped at; otherwise, return -1 as the index."""
        location, rect, index = self._check_drag_in_tabbar(pos)
        if location is _DropLocations.NONE:
            location, rect = self._check_drag_in_page(pos)
        return location, rect, index

    def _is_valid_drag_event(self, event):
        """Return if the QDropEvent `event` is valid for this widget."""
        return isinstance(event.source(), _NotebookTabBar)

    def insert_from_drag_info(self, index, drag_info):
        """Insert a widget stored in `drag_info` to index.
        Only add if that widget isn't already `index` in self"""
        if self.indexOf(drag_info.widget) != index:
            # Only add if inserted into a different index
            self.insertTab(index, drag_info.widget, drag_info.tabname)

    def add_from_drag_info(self, drag_info):
        """Add a widget stored in `drag_info` to end of the current tabs.
        Only add if that widget isn't already in `self`"""
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
            self.hide()
            self.deleteLater()
            self.notebook._current_tabwidget = None


class _NotebookTabBar(QtWidgets.QTabBar):
    """Tabbar used by `NotebookTabWidget`. Create a `QDrag` when a tab
    is dragged."""

    def __init__(self, tabwidget):
        super().__init__(tabwidget)
        self.drag_info = _DragInfo()
        self._tabwidget = tabwidget

    def mousePressEvent(self, event):
        """If it is a leftmouseclick, store a draginfo."""
        if event.button() == QtCore.Qt.LeftButton:
            tab_index = self.tabAt(event.pos())
            self.drag_info = _DragInfo(event.pos(), tab_index,
                                       self._tabwidget.widget(tab_index),
                                       self.tabText(tab_index))

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """If the mouse is pressed and has moved far enough, start a drag."""
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
        """If the button is the lmb, reset `self.drag_info`"""
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_info = _DragInfo()

        return super().mouseReleaseEvent(event)


class _DragInfo:
    """Store info about a drag.

    Attributes:
        - `initial_pos`: position of initial leftmouseclick,
        - `tab_index`: tab index that was clicked (or -1 if no tab clicked),
        - `widget`: widget corresponding to the `tab_index`,
        - `tabname`: tab name corresponding to the `tab_index`
        """

    def __init__(self, initial_pos=None, tab_index=-1, widget=None, tabname=''):
        super().__init__()

        self.initial_pos = initial_pos
        self.tab_index = tab_index
        self.widget = widget
        self.tabname = tabname


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()
    notebook = Notebook()
    for i in range(20):
        notebook.add_tab(QtWidgets.QPlainTextEdit(f'Page {i}'), f'Page {i}')
    window.setCentralWidget(notebook)
    window.show()
    app.exec_()
