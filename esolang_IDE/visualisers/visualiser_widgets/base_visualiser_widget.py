from PyQt5 import QtCore, QtWidgets


class BaseVisualiserWidget(QtWidgets.QWidget):
    """This class should be subclassed."""

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):
        # Should be overidden in a subclass
        pass

    def reset_visual(self):
        """Reset this data for the visualiser.
        This method does not update visual however. (`update_visual` should
        generally be called after this.)"""
        # Should be overidden in a subclass
        pass

    def configure_visual(self, visual_info):
        """Method should be called after every step.
        `visual_info` can be None. In that case, this method should
        do the same as `reset_visual`."""
        # Should be overidden in a subclass
        pass

    def update_visual(self):
        """Method should be called when the changes to the visualiser want
        to be displayed."""
        # Should be overidden in a subclass
        pass


class NoVisualiserWidget(BaseVisualiserWidget):
    pass
