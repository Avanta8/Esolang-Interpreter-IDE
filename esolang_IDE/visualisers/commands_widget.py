import enum
import functools
from PyQt5 import QtCore, QtWidgets


class ButtonType(enum.Enum):
    run = enum.auto()
    continue_ = enum.auto()
    step = enum.auto()
    pause = enum.auto()
    stop = enum.auto()
    back = enum.auto()
    jump_forwards = enum.auto()
    jump_backwards = enum.auto()


class CommandsWidget(QtWidgets.QWidget):

    button_clicked = QtCore.pyqtSignal(ButtonType)
    runspeed_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

        self.display_stopped()

    def init_widgets(self):
        buttons = self._create_buttons()
        speed = self._create_speed()
        jump = self._create_jump()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttons)
        layout.addWidget(speed)
        layout.addWidget(jump)
        self.setLayout(layout)

        self._connect_signals()

    def _create_buttons(self):
        self._run_button = QtWidgets.QPushButton('Run')
        self._continue_button = QtWidgets.QPushButton('Continue')
        self._step_button = QtWidgets.QPushButton('Step')
        self._pause_button = QtWidgets.QPushButton('Pause')
        self._back_button = QtWidgets.QPushButton('Back')
        self._stop_button = QtWidgets.QPushButton('Stop')
        self._grid_buttons = {
            self._run_button,
            self._step_button,
            self._pause_button,
            self._back_button,
            self._stop_button,
            self._continue_button,
        }

        self._button_layout = QtWidgets.QGridLayout()
        self._button_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        groupbox = QtWidgets.QGroupBox('Commands:')
        groupbox.setLayout(self._button_layout)
        return groupbox

    def _create_jump(self):
        jump_label = QtWidgets.QLabel('Steps:')
        self._jump_input = QtWidgets.QLineEdit()
        self._forwards_button = QtWidgets.QPushButton('Forward')
        self._backwards_button = QtWidgets.QPushButton('Backwards')

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(jump_label)
        top_layout.addWidget(self._jump_input)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self._backwards_button)
        bottom_layout.addWidget(self._forwards_button)

        jump_layout = QtWidgets.QVBoxLayout()
        jump_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        jump_layout.addLayout(top_layout)
        jump_layout.addLayout(bottom_layout)

        groupbox = QtWidgets.QGroupBox('Jump:')
        groupbox.setLayout(jump_layout)
        return groupbox

    def _create_speed(self):
        # QSlider defaults to a range of 0 - 99 inclusive
        self._speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._speed_checkbox = QtWidgets.QCheckBox('Faster')

        speed_layout = QtWidgets.QVBoxLayout()
        speed_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        speed_layout.addWidget(self._speed_slider)
        speed_layout.addWidget(self._speed_checkbox)

        groupbox = QtWidgets.QGroupBox('Runspeed:')
        groupbox.setLayout(speed_layout)
        return groupbox

    def _connect_signals(self):

        emit = self.button_clicked.emit
        self._run_button.clicked.connect(functools.partial(emit, ButtonType.run))
        self._continue_button.clicked.connect(
            functools.partial(emit, ButtonType.continue_)
        )
        self._stop_button.clicked.connect(functools.partial(emit, ButtonType.stop))
        self._step_button.clicked.connect(functools.partial(emit, ButtonType.step))
        self._back_button.clicked.connect(functools.partial(emit, ButtonType.back))
        self._pause_button.clicked.connect(functools.partial(emit, ButtonType.pause))
        self._forwards_button.clicked.connect(
            functools.partial(emit, ButtonType.jump_forwards)
        )
        self._backwards_button.clicked.connect(
            functools.partial(emit, ButtonType.jump_backwards)
        )

        self._speed_slider.valueChanged.connect(self.runspeed_changed.emit)
        self._speed_checkbox.stateChanged.connect(self.runspeed_changed.emit)

    def display_running(self):
        self._display_buttons(
            self._stop_button,
            self._pause_button,
        )

    def display_paused(self):
        self._display_buttons(
            self._stop_button,
            self._step_button,
            self._back_button,
            self._continue_button,
        )

    def display_stopped(self):
        self._display_buttons(
            self._run_button,
            self._step_button,
        )

    def _display_buttons(self, a=None, b=None, c=None, d=None):
        self._clear_buttons()
        for i, button in enumerate((a, b, c, d)):
            if button is not None:
                self._button_layout.addWidget(button, i // 2, i % 2)
                button.show()

    def _clear_buttons(self):
        """Remove all buttons."""
        for button in self._grid_buttons:
            if button.isVisible():
                self._button_layout.removeWidget(button)
                button.hide()

    def get_jump_input(self):
        return self._jump_input
