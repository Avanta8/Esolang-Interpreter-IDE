from PyQt5 import QtCore, QtGui, QtWidgets

from constants import FileTypes

from visualisers.commands_widget import CommandsWidget
from visualisers.io_widget import IOWidget


from visualisers.visualiser_widgets import NoVisualiserWidget, BrainfuckVisualiserWidget


class MainVisualiser(QtWidgets.QWidget):
    """Main visualiser widget that contains each panel that displays widgets.
    Contols what happens when a button is pressed."""

    filetype_to_visualiser = {
        FileTypes.NONE: NoVisualiserWidget,
        FileTypes.BRAINFUCK: BrainfuckVisualiserWidget,
    }

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.editor_page = parent

        self.init_widgets()
        self.set_runspeed()

        self.visualiser_stopped()

    def init_widgets(self):
        self.set_current_position(0, 0)

        self.run_timer = QtCore.QTimer(self)
        self.run_timer.timeout.connect(self.run_signal)

        self.visualiser_frame = NoVisualiserWidget(self)
        self.commands_frame = CommandsWidget(self)
        self.io_panel = IOWidget(self)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(self.visualiser_frame)
        self.splitter.addWidget(self.commands_frame)
        self.splitter.addWidget(self.io_panel)

        self.statusbar = QtWidgets.QStatusBar(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter, stretch=1)
        layout.addWidget(self.statusbar)
        self.setLayout(layout)

        self.commands_frame.button_pressed.connect(self.button_pressed)
        self.editor_page.code_text.key_during_visualisation.connect(
            self.key_during_visualisation
        )

    def set_filetype(self, filetype):
        visualiser_type = self.filetype_to_visualiser[filetype]
        if isinstance(self.visualiser_frame, visualiser_type):
            return

        # If the filetype is different, create a new visualiser
        # corresponding to `filetype`
        self.visualiser_frame.deleteLater()
        self.visualiser_frame = visualiser_type(self)
        self.splitter.insertWidget(0, self.visualiser_frame)

        self.io_panel.input_text.set_filetype(filetype)

    def set_current_position(self, position, chars):
        """Set the position in the `code_text` of the current command
        being executed.

        Arguments:
            - postition: index of start of command
            - chars: length of command in characters."""
        self._current_command_position = (position, chars)

    def highlight_current_position(self):
        """Highlight the current position in the code text."""
        self.editor_page.code_text.highlight_position(*self._current_command_position)

    def set_runspeed(self):
        """Method should be called whenever an option relating to runspeed is changed.
        Recalculate the runspeed."""
        if self.commands_frame.speed_checkbox.isChecked():
            runspeed = 10
            self.steps_skip = self.commands_frame.speed_slider.value() // 5
        else:
            value = self.commands_frame.speed_slider.value() + 1
            runspeed = int(1000 / (value * value * 0.0098 + 1))
            self.steps_skip = 0
        self.run_timer.setInterval(runspeed)

    def button_pressed(self):
        """Method should be called whenever a button is pressed.
        Remove all the error text."""
        self.io_panel.clear_error_text()
        self.editor_page.code_text.remove_errors()

    def command_step(self):
        """Step command"""
        self.visualiser_frame.step()
        self.visualiser_frame.display_visual()
        self.highlight_current_position()

    def command_run(self):
        """Run command"""
        self.run_timer.start()
        self.run_signal()

    def command_pause(self):
        """Pause command"""
        self.run_timer.stop()

    def command_stop(self):
        """Stop command"""
        self.run_timer.stop()
        self.visualiser_frame.stop()

    def command_back(self):
        """Back command"""
        self.visualiser_frame.back()
        self.visualiser_frame.display_visual()
        self.highlight_current_position()

    def command_jump_forwards(self, steps):
        """Jump forwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.visualiser_frame.step():
                succesful = False
                break
        else:
            succesful = True
        self.visualiser_frame.display_visual()
        self.highlight_current_position()
        return succesful

    def command_jump_backwards(self, steps):
        """Jump backwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.visualiser_frame.back():
                succesful = False
                break
        else:
            succesful = True
        self.visualiser_frame.display_visual()
        self.highlight_current_position()
        return succesful

    def run_signal(self):
        """Method called from `self.run_timer` timout."""
        success = self.command_jump_forwards(self.steps_skip + 1)
        if not success:
            self.commands_frame.display_paused()
            self.command_pause()

    def visualiser_restarted(self):
        """Method should be called whenever a new interpreter is started."""
        self.editor_page.code_text.visualisation_started()
        self.io_panel.output_text.clear()
        self.statusbar.showMessage('During execution')

    def visualiser_stopped(self):
        """Method should be called whenever a new interpreter is destroyed."""
        self.editor_page.code_text.visualisation_stopped()
        self.statusbar.showMessage('Visualiser not currently active')
        self.io_panel.input_text.restart()

    def set_error(self, message, location=None):
        """Set an error message `message`.
        If `location` is given, highlight it in the code text.
        `location` should be a tuple (start_position, no_of_chars)"""
        self.io_panel.set_error_text(message)
        if location is not None:
            self.editor_page.code_text.highlight_error(*location)

    def key_during_visualisation(self):
        """Key pressed in code text while intepreter is active."""
        self.io_panel.timed_error_text('Please stop visualiser before editing text')

    def get_code_text(self):
        return self.editor_page.get_text()

    def get_next_input(self):
        return self.io_panel.input_text.next_()

    def undo_input(self):
        self.io_panel.input_text.prev()

    def set_output(self, output):
        self.io_panel.output_text.set_text(output)

    def closed(self):
        """Method called when the visualiser containing `self` is closed."""
        self.commands_frame.display_paused()
        self.command_stop()
