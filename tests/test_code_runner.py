import itertools
from pathlib import Path

import pytest
from pytestqt import qtbot

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtTest import QTest

from esolang_IDE.controllers.runner_controller import RunnerController, _RunnerStatus
from esolang_IDE.code_text import CodeText
from esolang_IDE.code_runner import CodeRunner

from esolang_IDE.file_info import FileInfo

from esolang_IDE.filetypes import FileTypes

SHORT_TEST = False
SKIPTEXT = 'SHORT_TEST is True'
SAMPLE_PROGRAMS_PATH = (Path(__file__).parent / 'sample_programs').resolve()


def read_file(filename):
    return FileInfo.from_filepath((SAMPLE_PROGRAMS_PATH / filename).resolve()).read()


@pytest.fixture(autouse=True)
def setup(request, qtbot):

    code_text = CodeText()
    code_text.set_lexer(FileTypes.BRAINFUCK.to_lexer())

    runner = CodeRunner()

    controller = RunnerController(code_text, runner)
    controller.set_filetype(FileTypes.BRAINFUCK)

    request.cls.code_text = code_text
    request.cls.code_runner = runner
    request.cls.runner_controller = controller
    request.cls.qtbot = qtbot

    # code_text.show()
    # runner.show()


class _BaseTest:

    code_text: CodeText
    code_runner: CodeRunner
    runner_controller: RunnerController
    qtbot: qtbot.QtBot

    filename: str

    @pytest.fixture(autouse=True)
    def setup_text(self):
        self.source_code = read_file(self.filename)
        self.code_text.setText(self.source_code)

    def test_text_correct(self):
        assert self.source_code == self.code_text.text()

    def get_raw_output_text(self):
        return self.code_runner.get_output_text().toPlainText()

    def get_raw_input_text(self):
        return self.code_runner.get_input_text().toPlainText()

    def set_input_text(self, text):
        self.code_runner.get_input_text().setPlainText(text)

    def assert_need_input(self):
        assert self.runner_controller._status == _RunnerStatus.paused
        assert self.code_runner._statusbar.currentMessage() == 'Paused'
        assert self.code_runner._error_text.text() == 'Enter Input'

    def assert_stopped(self):
        assert self.runner_controller._status == _RunnerStatus.stopped
        assert self.code_runner._statusbar.currentMessage() == 'Stopped'

    def assert_empty_output(self):
        assert self.get_raw_output_text() == ''

    def run_code(self, timeout=1000):
        with self.qtbot.waitSignal(
            self.runner_controller._output_text.completed, timeout=timeout
        ) as blocker:
            self.runner_controller.run_code()

    def input_key_click(self, key):
        self.qtbot.keyClick(self.code_runner.get_input_text(), key)

    def input_key_clicks(self, keys):
        self.qtbot.keyClicks(self.code_runner.get_input_text(), keys)


class TestRunCode(_BaseTest):

    filename = 'hello world.b'

    def test_run_output_correct(self):
        self.run_code()

        assert self.get_raw_output_text() == 'Hello World!' * 20


class TestInfiniteOutput(_BaseTest):

    filename = 'forever output.b'
    _output = ''.join(chr(i) for i in range(1, 256, 2)).replace(
        '\r', '\n'
    )  # TextEdit converts \r to \n

    def test_run(self):
        self.runner_controller.run_code()

        self.qtbot.wait(500)

        with self.qtbot.waitSignal(
            self.runner_controller._output_text.completed,
            timeout=1000,
        ) as blocker:
            self.runner_controller.interrupt()

        assert len(self.get_raw_output_text()) >= 1000

        for a, b in zip(self.get_raw_output_text(), self._output):
            print(repr(a), repr(b))
            assert a == b

        assert self.get_raw_output_text().startswith(self._output)

    @pytest.mark.skipif(SKIPTEXT)
    def test_interrupt(self):

        for ms in itertools.islice(itertools.cycle((100, 200, 300)), 6):
            self.runner_controller.run_code()
            self.qtbot.wait(ms)

            with self.qtbot.waitSignal(
                self.runner_controller._output_text.completed,
                timeout=1000,
            ) as blocker:
                self.runner_controller.interrupt()

            self.assert_stopped()
            output = self.get_raw_output_text()
            assert output == ''.join(
                itertools.islice(itertools.cycle(self._output), len(output))
            )

    @pytest.mark.skipif(SKIPTEXT)
    def test_many_interrupt(self):

        for ms in itertools.repeat(20, 50):
            self.runner_controller.run_code()
            self.qtbot.wait(ms)

            with self.qtbot.waitSignal(
                self.runner_controller._output_text.completed,
                timeout=1000,
            ) as blocker:
                self.runner_controller.interrupt()

            self.assert_stopped()
            output = self.get_raw_output_text()
            assert output == ''.join(
                itertools.islice(itertools.cycle(self._output), len(output))
            )

    @pytest.mark.skipif(SKIPTEXT)
    def test_long_run(self):
        self.runner_controller.run_code()
        self.qtbot.wait(1000)
        with self.qtbot.waitSignal(
            self.runner_controller._output_text.completed,
            timeout=1000,
        ) as blocker:
            self.runner_controller.interrupt()

        self.assert_stopped()
        output = self.get_raw_output_text()
        print('block count:', self.code_runner.get_output_text().blockCount())
        assert output == ''.join(
            itertools.islice(itertools.cycle(self._output), len(output))
        )
        # assert 0

    @pytest.mark.skipif(SKIPTEXT)
    def test_keyboard_interrupt(self):

        for _ in range(5):
            for ms in range(10, 100, 10):
                self.runner_controller.run_code()
                self.qtbot.wait(ms)

                with self.qtbot.waitSignal(
                    self.runner_controller._output_text.completed,
                    timeout=1000,
                ) as blocker:
                    self.qtbot.keyClick(
                        self.code_runner.get_output_text(), 'c', QtCore.Qt.ControlModifier
                    )

                self.assert_stopped()
                assert len(self.get_raw_output_text()) > 0


class TestThreeInput(_BaseTest):
    filename = 'three input.b'

    def test_valid_input(self):

        self.qtbot.keyClicks(self.code_runner.get_input_text(), 'AbC')

        self.run_code()

        assert self.get_raw_output_text() == 'CbA'

    def test_unfinised_input(self):

        self.input_key_clicks('Ab')
        self.run_code()
        self.assert_need_input()
        self.assert_empty_output()

        # Make sure you can't delete any already processed input
        self.input_key_clicks('E')
        assert self.get_raw_input_text() == 'AbE'
        self.input_key_click(QtCore.Qt.Key_Backspace)
        self.input_key_click(QtCore.Qt.Key_Backspace)
        self.input_key_click(QtCore.Qt.Key_Backspace)
        self.input_key_clicks('h7fJHf' * 10)
        for _ in range(100):
            self.input_key_click(QtCore.Qt.Key_Backspace)
        assert self.get_raw_input_text() == 'Ab'

        # Now finish the input
        self.input_key_clicks('5')
        with self.qtbot.waitSignal(
            self.runner_controller._output_text.completed, timeout=1000
        ) as blocker:
            self.runner_controller.run_code()

        self.assert_stopped()
        assert self.get_raw_output_text() == '5bA'


class TestForeverInput(_BaseTest):
    filename = 'forever input.b'

    def test_full_program(self):

        self.run_code()
        self.assert_need_input()

        self.input_key_clicks('Hello_world!')
        self.run_code()
        self.assert_need_input()

        # testing that you can't delete processed input
        self.input_key_clicks('adfsadf')
        for _ in range(100):
            self.input_key_click(QtCore.Qt.Key_Backspace)

        self.input_key_clicks(R'end\0')

        assert self.get_raw_input_text() == R'Hello_world!end\0'

        self.run_code()
        self.assert_stopped()

        assert self.get_raw_output_text() == 'Hello_world!end'

        # test that can you use backspaces now
        for _ in range(5):
            self.input_key_click(QtCore.Qt.Key_Backspace)
        self.input_key_clicks(R'\0')
        assert self.get_raw_input_text() == R'Hello_world!\0'

        self.run_code()
        self.assert_stopped()
        assert self.get_raw_output_text() == 'Hello_world!'

    def test_escapes(self):

        # Valid escape characters are: \\, \n, \r, \t, \[0-9]{1,3}
        # \n is used by the textedit for a new line (so \r is converted to \n)

        self.input_key_clicks(R'g5\n\n\r\t\tabc\\\t\0')
        self.run_code()
        self.assert_stopped()

        assert self.get_raw_output_text() == 'g5\n\n\n\t\tabc\\\t'

        for _ in range(16):
            self.input_key_click(QtCore.Qt.Key_Backspace)
        assert self.get_raw_input_text() == R'g5\n' '\\'

        self.input_key_clicks(R'\65\34\143\10\243\2\56\87\57\107\0')

        assert self.get_raw_input_text() == R'g5\n\\65\34\143\10\243\2\56\87\57\107\0'

        self.run_code()
        self.assert_stopped()

        assert self.get_raw_output_text() == 'g5\n\\65' + ''.join(
            map(chr, [34, 143, 10, 243, 2, 56, 87, 57, 107])
        )


if __name__ == "__main__":
    pytest.main()
