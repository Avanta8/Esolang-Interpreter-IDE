from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes


class CommandsWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()
        self._connect_signals()

        self.pressed_stop()

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
        self.buttons = {self.run_button, self.step_button,
                        self.pause_button, self.back_button,
                        self.stop_button, self.continue_button}

        self.button_layout = QtWidgets.QGridLayout()
        self.button_layout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        # self.button_layout.setColumnStretch(0, 1)
        # self.button_layout.setColumnStretch(1, 1)

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

    def pressed_run(self):
        self._display_buttons(
            self.stop_button,
            self.pause_button,
        )

    def pressed_step(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def pressed_stop(self):
        self._display_buttons(
            self.run_button,
            self.step_button
        )

    def pressed_pause(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def pressed_back(self):
        self._display_buttons(
            self.stop_button,
            self.step_button,
            self.back_button,
            self.continue_button
        )

    def pressed_forwards(self):
        pass

    def pressed_backwards(self):
        pass

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


class IOWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):
        self.input_text = QtWidgets.QPlainTextEdit(self)
        self.output_text = QtWidgets.QPlainTextEdit(self)
        self.error_text = QtWidgets.QLineEdit(self)

        self.input_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.output_text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.output_text.setReadOnly(True)
        self.error_text.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Input:'))
        layout.addWidget(self.input_text)
        layout.addWidget(QtWidgets.QLabel('Output:'))
        layout.addWidget(self.output_text)
        layout.addWidget(self.error_text)
        self.setLayout(layout)


class VisualiserWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.init_widgets()

    def init_widgets(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError


class NoVisualiserWidget(VisualiserWidget):

    def init_widgets(self):
        pass


class MainVisualiser(QtWidgets.QSplitter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_widgets()

    def init_widgets(self):
        self.visualiser_frame = NoVisualiserWidget(self)
        self.commands_frame = CommandsWidget(self)
        self.io_panel = IOWidget(self)

        self.addWidget(self.visualiser_frame)
        self.addWidget(self.commands_frame)
        self.addWidget(self.io_panel)

    def set_filetype(self, filetype):
        pass
