from typing import Any, Callable, Optional

from dataclasses import dataclass

from PyQt5 import QtCore, QtWidgets

from esolang_IDE.code_text import CodeText
from esolang_IDE.visualisers import MainVisualiser

import esolang_IDE.interpreters as interpreters

from esolang_IDE.constants import FileTypes

from esolang_IDE.visualisers.commands_widget import ButtonType


"""
TODO:

- Many input commands close to each other is close as it updates the highligting
    after every single next char is processed.

    Instead, maybe manually update the highlighting instead, using a single shot
    timer as a blocker?
"""


@dataclass
class ModelData:

    output_text: str = ''
    command_position: tuple[int, int] = (0, 0)  # (start_position, num_chars)
    status_message: str = ''
    visual_data: Any = None

    def reset(self):
        self.output_text = ''
        self.command_position = (0, 0)
        self.status_message = ''
        self.visual_data = None


class WorkerThread(QtCore.QThread):

    iters: int
    fn: Callable

    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(interpreters.InterpreterError)

    def run(self):
        assert self.iters >= 1

        self._running = True
        fn = self.fn
        ret = None
        try:
            for _ in range(self.iters):
                ret = fn()
                if not self._running:
                    break
        except interpreters.InterpreterError as e:
            self.error.emit(e)
        finally:
            self.finished.emit(ret)

            # Drop reference to the interpreter  # Is this good to do or not?
            self.fn = None

    def start(self, priority=QtCore.QThread.InheritPriority, *, fn, iters):

        self.fn = fn
        self.iters = iters

        return super().start(priority=priority)

    def stop(self):
        self._running = False


class VisualiserController:
    def __init__(self, code_text: CodeText, visualiser: MainVisualiser):

        # TODO:
        # Refactor setting the runspeed

        self._code_text = code_text
        self._visualiser = visualiser

        self._model = Model(self)

        self._interpreter = None

        self._set_runspeed()
        self._connect_signals()

    def _connect_signals(self):
        self._commands_widget.runspeed_changed.connect(self._set_runspeed)
        self._commands_widget.button_clicked.connect(self._button_clicked)

        self._code_text.key_during_visualisation.connect(self._key_during_visualisation)

    def _button_clicked(self, button_type: ButtonType):
        self._clear_errors()

        # Run the method corresponding to which putton was pressed.
        {
            ButtonType.run: self._pressed_run,
            ButtonType.continue_: self._pressed_run,
            ButtonType.step: self._pressed_step,
            ButtonType.pause: self._pressed_pause,
            ButtonType.stop: self._pressed_stop,
            ButtonType.back: self._pressed_back,
            ButtonType.jump_forwards: self._pressed_forwards,
            ButtonType.jump_backwards: self._pressed_backwards,
        }[button_type]()

    def _pressed_run(self):
        self._commands_widget.display_running()

        self._code_text.visualisation_started()
        self._model.run()

    def _pressed_step(self):
        self._commands_widget.display_paused()

        self._code_text.visualisation_started()
        self._model.step(1)

    def _pressed_stop(self):
        self._commands_widget.display_stopped()

        self._model.stop()

        self._code_text.visualisation_stopped()

        # Maybe it would be better to put his somewhere else?
        self._input_text.restart()

    def _pressed_pause(self):
        self._commands_widget.display_paused()

        self._model.pause()

    def _pressed_back(self):
        self._commands_widget.display_paused()

        self._model.step(-1)

    def _pressed_forwards(self):
        self._commands_widget.display_paused()
        self._model.pause()

        self._code_text.visualisation_started()
        steps = self._get_jump_steps()
        if steps:
            self._model.step(steps)

    def _pressed_backwards(self):
        self._commands_widget.display_paused()
        self._model.pause()

        self._code_text.visualisation_started()
        steps = self._get_jump_steps()
        if steps:
            self._model.step(-steps)

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
        self._model._set_runspeed(
            self._commands_widget._speed_slider.value(),
            self._commands_widget._speed_checkbox.isChecked(),
        )

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

        if isinstance(error, interpreters.ProgramSyntaxError):
            self._model.stop()
            self._commands_widget.display_stopped()
        else:
            self._commands_widget.display_paused()

    def set_filetype(self, filetype: FileTypes):

        # TODO:
        # Check if filetype is the same as the current filetype, and don't
        # update it if it is the same.

        self._model.set_interpreter_type(filetype.to_interpreter())
        self._visualiser.set_visualiser_type(filetype.to_visualiser())
        self._input_text.set_decoder(filetype.to_input_decoder())

    def _key_during_visualisation(self):
        if self._model.is_active():
            self._io_widget.timed_error_text('Please stop visualiser before editing text')
        else:
            self._clear_errors()
            self._pressed_stop()

    def closed(self):
        """Should be called if the visualer window is closed."""
        self._clear_errors()
        self._pressed_stop()
        self.reset_visualiser()

    def reset_visualiser(self):
        self._visualiser_widget.reset_visual()
        self._visualiser_widget.update_visual()

    def get_visualiser(self):
        return self._visualiser

    def update_view(self):
        data = self._model.get_data()
        self._code_text.highlight_position(*data.command_position)
        self._output_text.set_text(data.output_text)
        self._visualiser.show_status_message(data.status_message)
        self._visualiser_widget.configure_visual(data.visual_data)
        self._visualiser_widget.update_visual()

    def get_source_code(self):
        return self._code_text.text()

    def next_input(self):
        return self._input_text.next_(2)

    def undo_input(self):
        self._input_text.prev(2)

    @property
    def _visualiser_widget(self):
        return self._visualiser.get_visualiser_widget()

    @property
    def _io_widget(self):
        return self._visualiser.get_io_widget()

    @property
    def _commands_widget(self):
        return self._visualiser.get_commands_widget()

    @property
    def _input_text(self):
        return self._io_widget.get_input_text()

    @property
    def _output_text(self):
        return self._io_widget.get_output_text()

    @property
    def _jump_input(self):
        return self._commands_widget.get_jump_input()


class Model:
    def __init__(self, controller: VisualiserController):
        self._controller = controller

        self._interpreter_type = None
        self._interpreter = None

        self._data = ModelData()

        self._worker = WorkerThread()
        self._worker.finished.connect(self._worker_finished)
        self._worker.error.connect(self._worker_error)

        self._run_timer = QtCore.QTimer()
        self._run_timer.timeout.connect(self._run_signal)

        self._run_steps = 0

        self._session_active = False

    def step(self, steps):
        assert isinstance(steps, int)
        assert steps != 0

        if not self._session_active:
            self._data.reset()
            self._controller.reset_visualiser()

            try:
                self.restart_interpreter()
            except interpreters.ProgramSyntaxError as e:
                self._worker_error(e)
                return
            else:
                self._session_active = True

        if steps > 0:
            fn = self._interpreter.step
        else:
            fn = self._interpreter.back

        self._worker.start(fn=fn, iters=abs(steps))
        self._data.status_message = 'During execution'

    def run(self):
        self._run_timer.start()
        self._run_timer.timeout.emit()

    def pause(self):
        self._run_timer.stop()

    def stop(self):
        self._data.status_message = 'Visualiser not currently active'
        self._run_timer.stop()
        self._worker.stop()
        self._session_active = False

        if not self._worker.isRunning():
            self._controller.update_view()

    def _run_signal(self):
        self.step(self._run_steps)

    def _set_runspeed(self, value: int, checked: bool):
        if checked:
            runspeed = 10
            self._run_steps = value // 5 + 1
        else:
            runspeed = int(1000 / ((value + 1) ** 2 * 0.0098 + 1))
            self._run_steps = 1
        self._run_timer.setInterval(runspeed)

    def restart_interpreter(self):
        if self._interpreter_type is None:
            raise RuntimeError('interpreter type is None')

        self._interpreter = self._interpreter_type(
            self._controller.get_source_code(),
            input_func=self._controller.next_input,
            undo_input_func=self._controller.undo_input,
            output_func=self._output_func,
        )

    def set_interpreter_type(self, interpreter_type: type[interpreters.BaseInterpreter]):
        self._interpreter_type = interpreter_type

    def _worker_finished(self, command_position):
        # Should this be a signal instead?

        if command_position is not None:
            self._data.command_position = command_position
        self._data.visual_data = self._interpreter.get_visual()

        self._controller.update_view()

    def _worker_error(self, error: interpreters.InterpreterError):
        self._controller.handle_interpreter_error(error)
        self._run_timer.stop()

    def _output_func(self, output: str):
        self._data.output_text = output

    def get_data(self) -> ModelData:
        return self._data

    def is_active(self) -> bool:
        return self._session_active
