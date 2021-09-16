from PyQt5 import QtCore, QtWidgets

from visualisers import (
    MainVisualiser,
    IOWidget,
    CommandsWidget,
    NoVisualiserWidget,
    BrainfuckVisualiserWidget,
)

import interpreters

from constants import FileTypes


class VisualiserController:

    _filetype_to_visualiser = {
        FileTypes.NONE: NoVisualiserWidget,
        FileTypes.BRAINFUCK: BrainfuckVisualiserWidget,
    }

    _filetype_to_interpreter = {
        FileTypes.NONE: interpreters.BaseInterpreter,
        FileTypes.BRAINFUCK: interpreters.BrainfuckInterpreter,
    }

    def __init__(self, code_text):

        self._io_widget = IOWidget()
        self._commands_widget = CommandsWidget()
        self._visualiser_widget = NoVisualiserWidget()

        self._code_text = code_text

        self._visualiser = MainVisualiser(
            visualiser_widget=self._visualiser_widget,
            commands_widget=self._commands_widget,
            io_widget=self._io_widget,
        )

        self._current_command_position = (0, 0)  # (start_position, num_chars)

        self._run_timer = QtCore.QTimer()

        # Change this later
        self._input_text = self._io_widget.input_text
        self._output_text = self._io_widget.output_text
        self._jump_input = self._commands_widget.jump_input

        self._interpreter = None

        self._set_runspeed()
        self._connect_signals()

    def _connect_signals(self):
        self._commands_widget.run_button.clicked.connect(self._pressed_run)
        self._commands_widget.continue_button.clicked.connect(self._pressed_run)
        self._commands_widget.step_button.clicked.connect(self._pressed_step)
        self._commands_widget.pause_button.clicked.connect(self._pressed_pause)
        self._commands_widget.back_button.clicked.connect(self._pressed_back)
        self._commands_widget.stop_button.clicked.connect(self._pressed_stop)
        self._commands_widget.forwards_button.clicked.connect(self._pressed_forwards)
        self._commands_widget.backwards_button.clicked.connect(self._pressed_backwards)

        self._commands_widget.speed_slider.valueChanged.connect(self._set_runspeed)
        self._commands_widget.speed_checkbox.stateChanged.connect(self._set_runspeed)

        self._code_text.key_during_visualisation.connect(self._key_during_visualisation)

        self._run_timer.timeout.connect(self._run_signal)

    def _pressed_run(self):
        self._clear_errors()
        self._commands_widget.display_running()

        self._run_timer.start()
        self._run_signal()

    def _pressed_step(self):
        self._clear_errors()
        self._commands_widget.display_paused()

        self.step()
        self._visualiser_widget.update_visual()
        self._highlight_current_position()

    def _pressed_stop(self):
        self._clear_errors()
        self._commands_widget.display_stopped()

        self._run_timer.stop()
        self.stop()

    def _pressed_pause(self):
        self._clear_errors()
        self._commands_widget.display_paused()

        self._run_timer.stop()

    def _pressed_back(self):
        self._clear_errors()
        self._commands_widget.display_paused()

        self.back()
        self._visualiser_widget.update_visual()
        self._highlight_current_position()

    def _pressed_forwards(self):
        self._pressed_pause()
        steps = self._get_jump_steps()
        if steps:
            self.jump_fowards(steps)

    def _pressed_backwards(self):
        self._pressed_pause()
        steps = self._get_jump_steps()
        if steps:
            self.jump_backwards(steps)

    def _clear_errors(self):
        self._io_widget.clear_error_text()
        self._code_text.remove_errors()

    def _get_jump_steps(self):
        try:
            return int(self._jump_input.text())
        except ValueError:
            self._io_widget.set_error_text('Invalid jump steps')
            return 0

    def _set_runspeed(self):
        if self._commands_widget.speed_checkbox.isChecked():
            runspeed = 10
            self._steps_skip = self._commands_widget.speed_slider.value() // 5
        else:
            value = self._commands_widget.speed_slider.value() + 1
            runspeed = int(1000 / (value * value * 0.0098 + 1))
            self._steps_skip = 0
        self._run_timer.setInterval(runspeed)

    def _run_signal(self):
        success = self.jump_fowards(self._steps_skip + 1)
        if not success:
            self._commands_widget.display_paused()
            self._run_timer.stop()

    def restart_interpreter(self):
        if self._interpreter_type is None:
            return False

        self._visualiser_widget.reset_visual()
        try:
            self._interpreter = self._interpreter_type(
                self._code_text.text(),
                input_func=self._input_text.next_,
                undo_input_func=self._input_text.prev,
                output_func=self._output_text.set_text,
            )
        except interpreters.InterpreterError as error:
            self.handle_interpreter_error(error)
            return False
        else:
            self._code_text.visualisation_started()
            self._output_text.clear()
            self._visualiser.show_status_message('During execution')
            return True

    def step(self):
        if self._interpreter is None:
            if not self.restart_interpreter():
                return False

        try:
            index, chars = self._interpreter.step()
        except interpreters.InterpreterError as error:
            self.handle_interpreter_error(error)
            return False
        else:
            self._visualiser_widget.configure_visual(self._interpreter.get_visual())
            self._current_command_position = (index, chars)
            return True

    def back(self):
        if self._interpreter is None:
            raise Exception(
                f'self._interpreter is None in {type(self)}.back. This shouldn\'t happen'
            )
            return False

        try:
            index, chars = self._interpreter.back()
        except interpreters.InterpreterError as error:
            self.handle_interpreter_error(error)
            return False
        else:
            self._visualiser_widget.configure_visual(self._interpreter.get_visual())
            self._current_command_position = (index, chars)
            return True

    def jump_fowards(self, steps):
        """Jump forwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.step():
                succesful = False
                break
        else:
            succesful = True
        self._visualiser_widget.update_visual()
        self._highlight_current_position()
        return succesful

    def jump_backwards(self, steps):
        """Jump backwards `steps` steps.
        Return whether jump was completed without errors from interpreter."""
        for i in range(steps):
            if not self.back():
                succesful = False
                break
        else:
            succesful = True
        self._visualiser_widget.update_visual()
        self._highlight_current_position()
        return succesful

    def handle_interpreter_error(self, error):
        message = None
        if isinstance(error, interpreters.ExecutionEndedError):
            message = 'Execution finished'
        elif isinstance(error, interpreters.NoPreviousExecutionError):
            message = 'No previous execution'
        elif isinstance(error, interpreters.NoInputError):
            message = 'Enter input'
        elif isinstance(error, interpreters.ProgramError):
            error_type = error.error
            if error_type is interpreters.ErrorTypes.UNMATCHED_OPEN_PAREN:
                message = 'Unmatched opening parentheses'
            elif error_type is interpreters.ErrorTypes.UNMATCHED_CLOSE_PAREN:
                message = 'Unmatched closing parentheses'
            elif error_type is interpreters.ErrorTypes.INVALID_TAPE_CELL:
                message = 'Tape pointer out of bounds'

        if message is None:
            raise error

        self._io_widget.set_error_text(message)
        if isinstance(error, interpreters.ProgramError):
            self._code_text.highlight_error(*error.location)

    def stop(self):
        self._interpreter = None
        self._code_text.visualisation_stopped()
        self._visualiser.show_status_message('Visualiser not currently active')
        self._input_text.restart()

    def _highlight_current_position(self):
        """Highlight the current position in the code text."""
        self._code_text.highlight_position(*self._current_command_position)

    def set_filetype(self, filetype):
        visualiser_type = self._filetype_to_visualiser[filetype]
        if isinstance(self._visualiser_widget, visualiser_type):
            return
        self._interpreter_type = self._filetype_to_interpreter[filetype]

        self._visualiser_widget.deleteLater()
        self._visualiser_widget = visualiser_type()

        self._visualiser.insert_visualiser_widget(self._visualiser_widget)

        self._input_text.set_filetype(filetype)

    def _key_during_visualisation(self):
        self._io_widget.timed_error_text('Please stop visualiser before editing text')

    def get_visualiser(self):
        return self._visualiser

    def set_command_position(self, position):
        self._current_command_position = position
