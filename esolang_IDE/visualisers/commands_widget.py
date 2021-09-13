from PyQt5 import QtCore, QtWidgets


class CommandsWidget(QtWidgets.QWidget):

    button_pressed = QtCore.pyqtSignal()

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.main_visualiser = parent

        self.init_widgets()
        self._connect_signals()

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

    def _create_buttons(self):
        self.run_button = QtWidgets.QPushButton('Run')
        self.continue_button = QtWidgets.QPushButton('Continue')
        self.step_button = QtWidgets.QPushButton('Step')
        self.pause_button = QtWidgets.QPushButton('Pause')
        self.back_button = QtWidgets.QPushButton('Back')
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.buttons = {
            self.run_button,
            self.step_button,
            self.pause_button,
            self.back_button,
            self.stop_button,
            self.continue_button,
        }

        self.button_layout = QtWidgets.QGridLayout()
        self.button_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

        groupbox = QtWidgets.QGroupBox('Commands:')
        groupbox.setLayout(self.button_layout)
        return groupbox

    def _create_jump(self):
        jump_label = QtWidgets.QLabel('Steps:')
        self.jump_input = QtWidgets.QLineEdit()
        self.forwards_button = QtWidgets.QPushButton('Forward')
        self.backwards_button = QtWidgets.QPushButton('Backwards')

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(jump_label)
        top_layout.addWidget(self.jump_input)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.backwards_button)
        bottom_layout.addWidget(self.forwards_button)

        jump_layout = QtWidgets.QVBoxLayout()
        jump_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        jump_layout.addLayout(top_layout)
        jump_layout.addLayout(bottom_layout)

        groupbox = QtWidgets.QGroupBox('Jump:')
        groupbox.setLayout(jump_layout)
        return groupbox

    def _create_speed(self):
        # QSlider defaults to a range of 0 - 99 inclusive
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_checkbox = QtWidgets.QCheckBox('Faster')

        speed_layout = QtWidgets.QVBoxLayout()
        speed_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(self.speed_checkbox)

        groupbox = QtWidgets.QGroupBox('Runspeed:')
        groupbox.setLayout(speed_layout)
        return groupbox

    def _connect_signals(self):
        self.run_button.clicked.connect(self.pressed_run)
        self.continue_button.clicked.connect(self.pressed_run)
        self.step_button.clicked.connect(self.pressed_step)
        self.pause_button.clicked.connect(self.pressed_pause)
        self.back_button.clicked.connect(self.pressed_back)
        self.stop_button.clicked.connect(self.pressed_stop)
        self.forwards_button.clicked.connect(self.pressed_forwards)
        self.backwards_button.clicked.connect(self.pressed_backwards)

        self.speed_slider.valueChanged.connect(self.main_visualiser.set_runspeed)
        self.speed_checkbox.stateChanged.connect(self.main_visualiser.set_runspeed)

    def pressed_run(self):
        self.button_pressed.emit()
        self.display_running()
        self.main_visualiser.command_run()

    def pressed_step(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_step()

    def pressed_stop(self):
        self.button_pressed.emit()
        self.display_stopped()
        self.main_visualiser.command_stop()

    def pressed_pause(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_pause()

    def pressed_back(self):
        self.button_pressed.emit()
        self.display_paused()
        self.main_visualiser.command_back()

    def pressed_forwards(self):
        self.pressed_pause()
        steps = self._get_jump_steps()
        if steps is not None:
            self.main_visualiser.command_jump_forwards(steps)

    def pressed_backwards(self):
        self.pressed_pause()
        steps = self._get_jump_steps()
        if steps is not None:
            self.main_visualiser.command_jump_backwards(steps)

    def display_running(self):
        self._display_buttons(
            self.stop_button,
            self.pause_button,
        )

    def display_paused(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button,
        )

    def display_stopped(self):
        self._display_buttons(
            self.run_button,
            self.step_button,
        )

    def _display_buttons(self, a=None, b=None, c=None, d=None):
        self._clear_buttons()
        for i, button in enumerate((a, b, c, d)):
            if button is not None:
                self.button_layout.addWidget(button, i // 2, i % 2)
                button.show()

    def _clear_buttons(self):
        """Remove all buttons."""
        for button in self.buttons:
            if button.isVisible():
                self.button_layout.removeWidget(button)
                button.hide()

    def _get_jump_steps(self):
        try:
            return int(self.jump_input.text())
        except ValueError:
            self.main_visualiser.set_error('Invalid jump steps')
            return None
